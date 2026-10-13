//! EffectCraft for Android.
//!
//! The same egui UI and engine as the desktop app (`apps/effectcraft`), hosted in a
//! NativeActivity through eframe/winit, drawn with wgpu on Vulkan. The desktop-only pieces
//! (native file dialogs, cpal audio output, the control server, window geometry) are left out;
//! the app starts with an empty project and keeps its settings in the app's private storage.
//!
//! Build the APK with `cargo apk build --release -p effectcraft-android`
//! (see `.github/workflows/android.yml`).
#![cfg(target_os = "android")]

use android_activity::AndroidApp;
use effectcraft_ui_egui::EffectcraftApp;

/// Wraps the shared egui app as an `eframe::App`.
struct Mobile {
    app: EffectcraftApp,
}

impl eframe::App for Mobile {
    fn logic(&mut self, ctx: &egui::Context, frame: &mut eframe::Frame) {
        self.app.logic(ctx, frame);
    }

    fn ui(&mut self, ui: &mut egui::Ui, frame: &mut eframe::Frame) {
        self.app.ui(ui, frame);
    }

    fn on_exit(&mut self) {
        self.app.on_exit();
    }

    fn raw_input_hook(&mut self, ctx: &egui::Context, raw_input: &mut egui::RawInput) {
        self.app.raw_input_hook(ctx, raw_input);
    }
}

/// The device asks for the adapter's own limits, textures capped at 16384 px (as on desktop):
/// phones' GPUs often offer less than eframe's default set.
fn wgpu_options() -> eframe::WgpuConfiguration {
    use eframe::egui_wgpu::WgpuSetup;
    let mut config = eframe::WgpuConfiguration::default();
    if let WgpuSetup::CreateNew(setup) = &mut config.wgpu_setup {
        setup.device_descriptor = std::sync::Arc::new(|adapter| {
            let limits = adapter.limits();
            eframe::wgpu::DeviceDescriptor {
                label: Some("EffectCraft device"),
                required_limits: eframe::wgpu::Limits { max_texture_dimension_2d: limits.max_texture_dimension_2d.min(16384), ..limits },
                ..Default::default()
            }
        });
    }
    config
}

#[unsafe(no_mangle)]
pub fn android_main(android: AndroidApp) {
    // logcat: `adb logcat -s EffectCraft`
    android_logger::init_once(android_logger::Config::default().with_tag("EffectCraft").with_max_level(log::LevelFilter::Info));
    effectcraft_engine::logging::install_panic_hook();
    log::info!("effectcraft {} (android): starting", env!("CARGO_PKG_VERSION"));

    // Settings and crash recovery live in the app's private data directory.
    let data_dir = android.internal_data_path();

    let options = eframe::NativeOptions { android_app: Some(android), wgpu_options: wgpu_options(), ..Default::default() };
    let result = eframe::run_native(
        "EffectCraft",
        options,
        Box::new(move |cc| {
            match &cc.wgpu_render_state {
                Some(rs) => log::info!("graphics: {:?}", rs.adapter.get_info()),
                None => log::info!("graphics: no wgpu device"),
            }
            let gpu_failures = effectcraft_ui_egui::gpu_failure::GpuFailureBridge::new(&cc.egui_ctx);
            if let Some(rs) = &cc.wgpu_render_state {
                let errors = gpu_failures.clone();
                rs.device.on_uncaptured_error(std::sync::Arc::new(move |error| {
                    let message = format!("uncaptured GPU error: {error}");
                    if errors.report(&message, false) {
                        log::error!("{message}");
                    }
                }));
                let lost = gpu_failures.clone();
                rs.device.set_device_lost_callback(move |reason, message| {
                    lost.report(&format!("GPU device lost ({reason:?}): {message}"), true);
                });
            }
            let mut session = effectcraft_host::session();
            session.check_footage_on_open = true;
            session.autosave.background = true;
            if let Some(dir) = data_dir {
                session.config = Some(std::sync::Arc::new(effectcraft_engine::config::DirConfig::new(dir)));
            }
            session.load_settings();
            let mut app = EffectcraftApp::new(session);
            app.set_gpu_failure_bridge(gpu_failures);
            log::info!("app created");
            Ok(Box::new(Mobile { app }))
        }),
    );
    if let Err(e) = result {
        log::error!("EffectCraft couldn't start its window: {e}");
    }
}

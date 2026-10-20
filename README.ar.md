<div dir="rtl">

<p align="center">
  <img src="docs/logo.png" alt="BlockComet Launcher" width="140">
</p>

<h1 align="center">مشغّل BlockComet</h1>

<p align="center">
  مشغّل ماينكرافت: نسخة جافا لأندرويد، بنسخ Fabric جاهزة للّعب، وواجهة عربية كاملة، وتخصيص عميق.<br>
  <a href="README.md">English</a> · <a href="docs/CUSTOMIZING.md">التخصيص</a> · <a href="docs/BUILDING.md">البناء</a> ·
  <a href="docs/ARCHITECTURE.md">كيف يعمل</a> · <a href="CHANGELOG.md">سجل التغييرات</a>
</p>

> **غير تابع لـ Mojang ولا Microsoft.** ماينكرافت غير مضمّنة. تحتاج حساب ماينكرافت: نسخة جافا يملك اللعبة. برنامج حر
> بترخيص LGPL-3.0، مبني على [Copper Launcher](https://github.com/CopperLauncher/Copper-Android).

## التحميل

| | |
|---|---|
| الإصدار المستقر | [`BlockComet.apk`](https://github.com/justaguyLV/effectcraft/releases/latest/download/BlockComet.apk) (يظهر بعد أول إصدار `v*`) |
| آخر بناء من الفرع الرئيسي | [`BlockComet.apk`](https://github.com/justaguyLV/effectcraft/releases/download/copper-latest/BlockComet.apk) |
| كل الإصدارات | https://github.com/justaguyLV/effectcraft/releases |

يعمل على أندرويد 6.0 (API 23) وما فوق. ثبّت الملف (اسمح بالتثبيت من مصدر خارجي للمتصفح أو مدير الملفات)، وافتح المشغّل،
وسجّل الدخول بحساب Microsoft، واختر نسخة من الشريط السفلي، واضغط **ابدأ اللعب**.

كل إصدار يحمل أيضًا ملف `THIRD_PARTY_NOTICES.txt`، ونفس النص داخل التطبيق في **حول ← التراخيص**.

## ما بداخله

**نسخ جاهزة للّعب.** عند أول تشغيل ينشئ المشغّل نسخة «Meteor *إصدار*» لكل من ماينكرافت 1.20.1 و1.20.2 و1.20.4 و1.20.6
و1.21.1 وأحدث الإصدارات التي استطاع البناء تجهيزها. في كل واحدة أحدث Fabric Loader مستقر، وFabric API، و
[Meteor Client](https://github.com/MeteorDevelopment/meteor-client)، ومودات الأداء المتوفرة لذلك الإصدار: FerriteCore وLithium
وModernFix وKrypton وNoisium وMemoryLeakFix وScalableLux. قائمة المودات في كل نسخة موجودة في **حول ← التراخيص**.

**التخصيص** (الإعدادات ← مظهر المشغّل):

* **استوديو الألوان:** عشرة ألوان بقيم HEX / RGB دقيقة، وستة قوالب جاهزة، ومعاينة مباشرة. الألوان الدقيقة تحتاج أندرويد 11
  وما فوق، وما قبله يستعمل أقرب نمط جاهز.
* **الخلفية والأسطح** (أبيض، رمادي فاتح، جرافيت، أسود كامل)، و**استدارة الزوايا**، و**20 خطًا جاهزًا**، و**استيراد أي ملف خط
  `.ttf` / `.otf`** ليكون خط المشغّل.
* **مشاركة مظهري:** يحفظ ألوانك وخطك ولغتك وخلفيتك (صورة أو فيديو) في ملف واحد؛ يستورده صديقك فيحصل على المظهر نفسه.
* خلفية مخصصة للمشغّل (صورة أو GIF أو فيديو)، وحركات، وإجبار الوضع الأفقي.

**اللغات.** 46 لغة قابلة للاختيار من التطبيق، وواجهة عربية كاملة من اليمين لليسار (بخط Tajawal ليكون العربي واللاتيني
بتصميم واحد).

**إصلاحات فوق Copper.** صارت منطقة لمس شريط العناصر مطابقة للشريط الحقيقي (182 × 22 بكسل واجهة)، مع خيار يرسم مربعًا أحمر
فوقها (الإعدادات ← مظهر المشغّل ← «إظهار منطقة لمس شريط العناصر») لمعرفة أين تقع الضغطات.

**صفحة «حول» داخل التطبيق** بدل رابط الويب القديم، وفيها عنوان الكود المصدري والتراخيص وزر ديسكورد.

## لقطة

<p align="center"><img src="docs/screenshots/main-ar.png" alt="الشاشة الرئيسية بالعربية" width="520"></p>

## الحالة والحدود

* بُني واختُبر في محاكي أندرويد 11 (x86_64) على GitHub Actions: التشغيل والشاشات والتخطيط العربي. **لم يُجرَّب** على
  مجموعة واسعة من الأجهزة الحقيقية. افتح بلاغًا (issue) مع طراز جهازك وإصدار أندرويد إن بدا شيء غير سليم.
* Meteor Client عميل مساعد («هاك»). كثير من السيرفرات تمنعه، وأنت المسؤول عن مكان استخدامه. وقوائمه بالإنجليزية.
* Sodium غير مضمّن عمدًا: يحتاج OpenGL أقوى مما تقدمه كثير من الجوالات. تقدر تضيفه من *تصفّح المحتوى*.
* المشغّل لا يشغّل نسخة من ماينكرافت بدون حساب مرخّص، ولا شيء هنا يساعد في ذلك.

## البناء

المستودع يحوي **وصفة بناء** وليس نسخة من كود Copper: الـ workflow ينزّل Copper بنسخة (commit) محددة، ويطبّق سكربتات BlockComet،
ويبني الـ APK على GitHub Actions وينشره. راجع [docs/BUILDING.md](docs/BUILDING.md) لبناء نسختك أو توقيعها بمفتاحك أو تحديث
النسخة المثبّتة، و[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) لمعرفة ما يغيّره كل سكربت.

## الترخيص والشكر

BlockComet برنامج حر بترخيص **GNU LGPL v3** ([LICENSE](LICENSE) و[COPYING](COPYING)). المصدر اللازم لإعادة بناء التطبيق هو هذا
المستودع مع نسخة المصدر الأصلي المثبّتة في الـ workflow. مبني على Copper Launcher وMojoLauncher وPojavLauncher، ومعه
Meteor Client (GPL-3.0) وFabric والمودات المذكورة في [NOTICE.md](NOTICE.md). الخطوط من Google Fonts (ترخيص SIL OFL 1.1،
وUbuntu بترخيصه الخاص).

## المجتمع

ديسكورد: https://discord.gg/5fhcfW2Ge · الأخطاء والأفكار: [issues](https://github.com/justaguyLV/effectcraft/issues) ·
للمساهمة: [CONTRIBUTING.md](CONTRIBUTING.md) · الأمان: [SECURITY.md](SECURITY.md)

</div>

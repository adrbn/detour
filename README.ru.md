<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/hero-light-ru.svg">
  <img src="docs/assets/hero-ru.svg" width="100%" alt="FL Studio играет на Mac. Его звук не идёт на динамики Mac и чисто доходит до AirPods через значок Detour в строке меню.">
</picture>

<p align="center">
  <img src="docs/assets/icon.png" width="96" height="96" alt="Значок Detour">
</p>

<p align="center">
  <b>AirPods с FL Studio на Mac, без треска.</b><br>
  Маленькое приложение для строки меню, которое выводит звук FL Studio в Bluetooth-наушники с верной высотой тона и без щелчков.
</p>

<p align="center">
  <a href="https://github.com/adrbn/detour/releases/latest"><img src="docs/assets/buttons/download-ru.svg" height="56" alt="Скачать Detour для macOS бесплатно"></a>
  &nbsp;
  <a href="#как-это-работает"><img src="docs/assets/buttons/how-ru.svg" height="56" alt="Как это работает"></a>
  &nbsp;
  <a href="https://github.com/adrbn/detour/issues/new"><img src="docs/assets/buttons/feedback-ru.svg" height="56" alt="Сообщить об ошибке или предложить приложение"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/macOS-14.2%2B-E8590C?style=flat-square&logo=apple&logoColor=white&labelColor=1c1c1e" alt="macOS 14.2 или новее">
  <img src="https://img.shields.io/badge/Apple%20silicon-%D0%BD%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D0%BE-E8590C?style=flat-square&labelColor=1c1c1e" alt="Нативно на Apple silicon">
  <a href="https://github.com/adrbn/detour/releases/latest"><img src="https://img.shields.io/github/v/release/adrbn/detour?style=flat-square&label=%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%8F&color=E8590C&labelColor=1c1c1e" alt="Последняя версия"></a>
  <img src="https://img.shields.io/badge/%D1%81%D0%B5%D1%82%D1%8C-%D0%BD%D0%B5%D1%82-E8590C?style=flat-square&labelColor=1c1c1e" alt="Никаких сетевых запросов">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F-MIT-E8590C?style=flat-square&labelColor=1c1c1e" alt="Лицензия MIT"></a>
</p>

<p align="center">
  Бесплатно и с открытым кодом · подписано и нотаризовано · macOS 14.2 или новее на Apple silicon<br>
  <a href="README.md">English</a> · <a href="README.fr.md">Français</a> · <a href="README.es.md">Español</a> · <a href="README.de.md">Deutsch</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt-BR.md">Português</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh-Hans.md">简体中文</a> · <b>Русский</b>
</p>

---

## Проблема

Вы открываете FL Studio на Mac, вставляете AirPods, и проект звучит не так:

- **треск и щелчки** по всему миксу, даже на одном сэмпле;
- **ноты чуть фальшивят**: высота тона смещена, иногда плавает;
- тот же проект звучит **идеально на динамиках MacBook**.

Обычные советы не помогают. Мы попробовали каждый: буфер побольше, 48 кГц, вход «none», агрегатное устройство, другие аудионастройки FL. Звук остаётся испорченным, потому что дело не в настройках. Когда выход FL Studio направлен на AirPods, он плохо рендерит звук, а AirPods забирают аудио неравномерными рывками, и всё, что синхронизируется с их часами, наследует эти рывки.

Есть ещё ловушка, которая всё усугубляет. Выход FL Studio **«Default audio device»** следует за устройством Mac по умолчанию, поэтому FL переключается на AirPods при каждом их подключении, даже если вы уже выбрали динамики.

## Решение

Detour оставляет FL Studio на динамиках Mac, где он звучит правильно, глушит динамики и отправляет тот же звук в AirPods с верной высотой тона и без щелчков. Вы слышите в наушниках, как проект звучит на самом деле, и в FL Studio ничего менять не нужно.

> Detour нужен для прослушивания, сочинения и сведения. Bluetooth всегда добавляет задержку, поэтому для записи вокала или игры в такт по-прежнему лучше проводные наушники.

## Что делает Detour

<table>
  <tr>
    <td><img src="docs/assets/card-clean-ru.svg" width="100%" alt="Волна с треском становится чистой"></td>
    <td><img src="docs/assets/card-pitch-ru.svg" width="100%" alt="Стрелка тюнера встаёт точно на ноту"></td>
    <td><img src="docs/assets/card-ears-ru.svg" width="100%" alt="AirPods вынули и вставили обратно, звук возвращается"></td>
  </tr>
  <tr>
    <td><img src="docs/assets/card-silent-ru.svg" width="100%" alt="Динамики Mac молчат, пока вы слушаете"></td>
    <td><img src="docs/assets/card-menu-ru.svg" width="100%" alt="Меню Detour: отправка, ожидание FL Studio, затем предупреждение с решением"></td>
    <td><img src="docs/assets/card-apps-ru.svg" width="100%" alt="Пункт «Приложение» в меню Detour: FL Studio, Музыка, затем Safari"></td>
  </tr>
</table>

## Возможности

**Звук**
- Чистый звук FL Studio в AirPods: без треска, без щелчков, с верной высотой тона.
- Detour читает FL Studio по ровным часам динамиков и подаёт звук в AirPods из буфера на 100 мс, так что неровный ритм Bluetooth никогда не доходит до вашей музыки.
- Динамики Mac молчат всё время, в том числе когда AirPods не в ушах.

**Каждый день**
- Выньте AirPods и вставьте обратно: звук сам вернётся меньше чем за секунду.
- Начинает отправку, как только FL Studio играет, и тихо ждёт, когда не играет.
- Предупреждает, если FL Studio сам переключился на AirPods (его настройка «Default audio device» следует за ними), и подсказывает, что изменить.
- Живёт в строке меню. Ни окна, ни значка в Dock.

**Выбор**
- По умолчанию FL Studio; любое другое приложение со звуком можно выбрать в меню.
- Любой Bluetooth-выход: первый подключённый или тот, что вы выберете.

## Начало работы

1. **[Скачайте Detour](https://github.com/adrbn/detour/releases/latest)**, откройте `.dmg` и перетащите Detour в папку «Программы».
2. В FL Studio откройте **Options › Audio settings** и выберите в **Output** динамики Mac (например, *Динамики MacBook Pro*). Не «Default audio device»: он следует за AirPods.
3. Откройте Detour. Когда macOS спросит, разрешите доступ в **Системные настройки › Конфиденциальность и безопасность › Запись экрана и системного звука**.
4. Вставьте AirPods и запустите воспроизведение в FL Studio.

Значок наушников в строке меню показывает маленькие часы, пока Detour ждёт, и знак предупреждения, когда нужно ваше вмешательство. Просто наушники означают, что звук идёт в AirPods.

## Как это работает

FL Studio чисто рендерит звук на динамиках Mac и плохо, когда его выход направлен на AirPods. Мы измерили, почему очевидные решения не работают: AirPods забирают аудио неравномерными рывками (от 48 128 до 50 688 сэмплов от секунды к секунде, тогда как ровное устройство берёт 48 000), и всё, что синхронизируется с их часами, наследует эти колебания.

Поэтому Detour никогда не позволяет AirPods задавать темп:

1. **Process tap** (macOS 14.2+) захватывает выход FL Studio и глушит его на динамиках.
2. Tap читается по **часам динамиков**, тем же, по которым рендерит FL Studio.
3. Звук попадает в **буфер на 100 мс**. AirPods забирают из него в своём темпе, а очень медленная коррекция (не больше 0,5 %, усреднённая за несколько секунд) удерживает уровень буфера. Это намного ниже того, что ухо слышит как изменение высоты тона.

Тестовый тон 1 кГц, пройдя всю цепочку, выходит без единого щелчка, с частотой 1000,4 Гц.

## Частые вопросы

**Работает ли это с Ableton Live, Logic или другими приложениями?**
Выберите приложение в меню Detour. Пока протестирован только FL Studio 2026; отзывы о других приложениях ждём в issues.

**А другие Bluetooth-наушники?**
Detour работает с любым Bluetooth-выходом. Он протестирован с AirPods Pro 2.

**Какую задержку он добавляет?**
Около десятой доли секунды сверх собственной Bluetooth-задержки AirPods. Подходит для прослушивания и сведения, но не для записи в такт.

**Он что-нибудь записывает?**
Нет. Звук идёт от tap к наушникам в памяти и никогда не сохраняется. Detour не делает никаких сетевых запросов.

## Требования

- macOS 14.2 Sonoma или новее (process taps)
- Mac с Apple silicon
- Bluetooth-наушники

## Сборка из исходников

```bash
git clone https://github.com/adrbn/detour.git
cd detour
swift test
./scripts/build.sh            # собирает и подписывает build/Detour.app
```

`NOTARY_PROFILE=<профиль> ./scripts/build.sh` также нотаризует приложение и собирает `.dmg`. Иллюстрации README генерирует `python3 docs/assets/make_svgs.py`.

## Поддержка

Detour бесплатен. Если он спасает ваши сессии, можете угостить меня кофе.

<p>
  <a href="https://ko-fi.com/adrbn"><img src="docs/assets/buttons/kofi-ru.svg" height="48" alt="Угостить меня кофе на Ko-fi"></a>
</p>

## Лицензия

MIT: используйте, изменяйте, распространяйте, сохраняя уведомление об авторских правах.

<sub>Detour не связан ни с Image-Line, ни с Apple. FL Studio является товарным знаком Image-Line Software; AirPods и macOS являются товарными знаками Apple Inc.</sub>

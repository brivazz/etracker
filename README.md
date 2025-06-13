### Проект умеет:
- 📥 Добавлять траты,
- 🔎 Фильтровать по датам,
- 📊 Показывать статистику,
- 📤 Экспортировать в CSV.


### ✅ Пример запуска
```
$ python main.py
```

### Бот умеет:
- принимать расходы с выбором категории,
- повторять последние траты,
- показывать статистику.
- Отображает расходы по категориям в виде красивой диаграммы.
- Отправляет PNG-файл прямо в Telegram.


**Router**
- умеет регистрировать хендлеры с @router.message(...) и @router.callback(...),
- поддерживает Enum, str, regex, объединение значений и автоматическую маршрутизацию,
- оборачивает хендлеры в middleware (например, inject_user()),
- при вызове хендлера распознаёт параметры коллбэка через parse_callback_data() и подставляет их.

🤖 **BotService**
- регистрирует все callback и message хендлеры централизованно в register_handlers(),
- использует оркестраторы (AddOrchestrator, StatsOrchestrator, и т.п.) как единицы бизнес-логики,
- умеет сам разруливать входящие callback’и по Enum + params,
- добавлен @router.message("/start"), и он работает как обычный хендлер.


📦 **Модульность**
- Модули handlers, orchestrators, services — разделены,
- Используется autoimport() — удобный способ подгрузить все модули хендлеров без ручного импорта,
- Хендлеры регистрируются через один BotService, что облегчает тестирование и масштабирование.


| Кнопка                     | Состояние FSM            | Пояснение                                |
| -------------------------- | ------------------------ | ---------------------------------------- |
| ➕ Добавить трату           | `ADD_EXPENSE`            | Показывает категории                     |
| Название категории         | `WAITING_FOR_AMOUNT`     | После выбора — ожидаем сумму             |
| Сумма                      | `EXPENSE_RECORDED`       | Подтверждение                            |
| ✏️ Редактировать последнюю | `EDIT_LAST_EXPENSE`      | Переход к выбору поля для редактирования |
| Повторить последнюю        | `REPEAT_LAST_EXPENSE`    | Повторный ввод                           |
| Удалить последнюю          | `DELETE_LAST_EXPENSE`    | Запрос на удаление                       |
| 📊 Статистика              | `SHOW_STATS` (не явно)   | Не меняет состояние                      |
| 📄 История трат            | `SHOW_HISTORY` (не явно) | Не меняет состояние                      |

### Архитектура
- Orchestrators управляют координацией use-case'ов.
- DTOs и Mappers обеспечивают преобразование между слоями.
- Unit of Work из application подключается к реализациям в infrastructure.
- Factories инстанцируют сервисы или зависимости.
- Domain Services содержат бизнес-логику.
- Repositories из domain абстрактны, а реализация — в infrastructure.

![Диаграмма](https://www.plantuml.com/plantuml/png/RL7DRl8m4BpxAIo-mtVYnhKL5AY41ABbHnmg3fQpIIqSRxJUL49LtxqH2SQfurDsPZApsfbwLiHrQOM_65SfKgKaqAnSOK5-2zcy5wKl1M7jiZbQ9FaF86y9f0oe0oUJYVWHuhzyQfvSEGRAbGP_cqNLUAW2vEX1Z3hxZmDOA9hWne_FBRHRxWzozhOwHvQpgh96ApRev5fTWVuu9tm8s9B-1C-a6Cbt2Ol3zlwvKLK5WNXLkf4PkCz7PrXYBaz8btYT1PRA36yIg7Y9fMF33zjEimVwCZgWEwZGctj-VCwSb6UgDTS4Ww6990xVlwzdjZb2UPKRpC3wSuBVebFuYATuaJaw1veDkgxOVdjoF7vExXtQ7AP57sX5RJ-3LEXhc8tx6fR45OimT6HQJD-n5VLxIlvfHQ7nGK7Y8g8vIDA24YXHXehJpTDgf-2okhI_)


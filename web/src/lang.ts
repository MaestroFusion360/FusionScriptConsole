export type LangKey = "en" | "ru";

export type LangOption = { label: string; value: LangKey };

export type Texts = {
  app: {
    title: string;
    version: string;
    footer: string;
    authorUrl: string;
    brand: string;
    subtitle: string;
    fields: {
      serverUrlLabel: string;
      serverUrlPlaceholder: string;
      apiKeyLabel: string;
      apiKeyPlaceholder: string;
      scriptNameLabel: string;
      scriptNamePlaceholder: string;
    };
    dialog: {
      saveTitle: string;
      deleteTitle: string;
      saveMessage: string;
      deleteMessage: string;
      nameRequired: string;
    };
    status: {
      idle: string;
      running: string;
      ok: string;
      error: string;
    };
    serverStatus: {
      online: string;
      offline: string;
    };
    sections: {
      pythonScript: string;
      output: string;
    };
    hints: {
      runShortcut: string;
      noOutput: string;
    };
    buttons: {
      save: string;
      delete: string;
      exportAll: string;
      clearOutput: string;
      run: string;
      toggleTheme: string;
    };
    checkbox: {
      wrapInRun: string;
      autoImport: string;
    };
    messages: {
      running: string;
      okNoOutput: string;
      unknownError: string;
      requestFailedPrefix: string;
      clipboardFailed: string;
      invalidServerUrl: string;
      httpPrefix: string;
      emptyResponse: string;
    };
    defaults: {
      serverUrl: string;
      scriptName: string;
      legacyName: string;
      exportFileName: string;
      defaultCode: string;
    };
    language: {
      label: string;
      options: LangOption[];
    };
  };
};

export const TEXTS: Record<LangKey, Texts> = {
  ru: {
    app: {
      title: "Fusion Script Console",
      version: "v0.0.9",
      footer: "(c) 2025 MaestroFusion360",
      authorUrl: "https://github.com/MaestroFusion360/FusionScriptConsole",
      brand: "Fusion API Server",
      subtitle: "Отправляйте Python в Fusion 360 и читайте вывод.",
      fields: {
        serverUrlLabel: "URL сервера",
        serverUrlPlaceholder: "http://127.0.0.1:9100/api",
        apiKeyLabel: "API ключ",
        apiKeyPlaceholder: "Введите API ключ",
        scriptNameLabel: "Имя скрипта",
        scriptNamePlaceholder: "Мой скрипт",
      },
      dialog: {
        saveTitle: "Сохранить скрипт",
        deleteTitle: "Удалить скрипт",
        saveMessage: "Сохранить текущий скрипт в локальное хранилище.",
        deleteMessage:
          "Удалить выбранный скрипт из списка и очистить редактор?",
        nameRequired: "Имя обязательно.",
      },
      status: {
        idle: "Ожидание",
        running: "Выполняется",
        ok: "Готово",
        error: "Ошибка",
      },
      serverStatus: {
        online: "Онлайн",
        offline: "Оффлайн",
      },
      sections: {
        pythonScript: "Python скрипт",
        output: "Вывод",
      },
      hints: {
        runShortcut: "Ctrl+Enter для запуска",
        noOutput: "Вывода пока нет",
      },
      buttons: {
        save: "Сохранить скрипт",
        delete: "Удалить скрипт",
        exportAll: "Экспортировать все скрипты",
        clearOutput: "Очистить вывод",
        run: "Запустить скрипт",
        toggleTheme: "Переключить тему",
      },
      checkbox: {
        wrapInRun: "Оборачивать в def run()",
        autoImport: "Auto-import adsk.core/fusion/cam",
      },
      messages: {
        running: "Выполняется...",
        okNoOutput: "OK (нет вывода)",
        unknownError: "Неизвестная ошибка",
        requestFailedPrefix: "Запрос не выполнен: ",
        clipboardFailed: "Не удалось скопировать в буфер",
        invalidServerUrl: "Некорректный URL сервера",
        httpPrefix: "HTTP",
        emptyResponse: "(пустой ответ)",
      },
      defaults: {
        serverUrl: "http://127.0.0.1:9100/api",
        scriptName: "Мой скрипт",
        legacyName: "Без названия",
        exportFileName: "fusion-scripts.txt",
        defaultCode: `import adsk.core


def run(context):
    app = adsk.core.Application.get()
    app.log(app.activeDocument.name)
    return app.activeDocument.name
`,
      },
      language: {
        label: "Язык",
        options: [
          { label: "Русский", value: "ru" },
          { label: "English", value: "en" },
        ],
      },
    },
  },
  en: {
    app: {
      title: "Fusion Script Console",
      version: "v0.0.9",
      footer: "(c) 2025 MaestroFusion360",
      authorUrl: "https://github.com/MaestroFusion360/FusionScriptConsole",
      brand: "Fusion API Server",
      subtitle: "Send Python to Fusion 360 and read the output.",
      fields: {
        serverUrlLabel: "Server URL",
        serverUrlPlaceholder: "http://127.0.0.1:9100/api",
        apiKeyLabel: "API Key",
        apiKeyPlaceholder: "Enter API key",
        scriptNameLabel: "Script name",
        scriptNamePlaceholder: "My script",
      },
      dialog: {
        saveTitle: "Save script",
        deleteTitle: "Delete script",
        saveMessage: "Save the current script to local storage under a name.",
        deleteMessage:
          "Delete the selected script from the list and clear the editor?",
        nameRequired: "Name is required.",
      },
      status: {
        idle: "Idle",
        running: "Running",
        ok: "Ready",
        error: "Error",
      },
      serverStatus: {
        online: "Online",
        offline: "Offline",
      },
      sections: {
        pythonScript: "Python script",
        output: "Output",
      },
      hints: {
        runShortcut: "Ctrl+Enter to run",
        noOutput: "No output yet",
      },
      buttons: {
        save: "Save script",
        delete: "Delete script",
        exportAll: "Export all scripts",
        clearOutput: "Clear output",
        run: "Run script",
        toggleTheme: "Toggle theme",
      },
      checkbox: {
        wrapInRun: "Wrap in def run()",
        autoImport: "Auto-import adsk.core/fusion/cam",
      },
      messages: {
        running: "Running...",
        okNoOutput: "OK (no output)",
        unknownError: "Unknown error",
        requestFailedPrefix: "Request failed: ",
        clipboardFailed: "Clipboard write failed",
        invalidServerUrl: "Invalid server URL",
        httpPrefix: "HTTP",
        emptyResponse: "(empty response)",
      },
      defaults: {
        serverUrl: "http://127.0.0.1:9100/api",
        scriptName: "My script",
        legacyName: "Untitled",
        exportFileName: "fusion-scripts.txt",
        defaultCode: `import adsk.core


def run(context):
    app = adsk.core.Application.get()
    app.log(app.activeDocument.name)
    return app.activeDocument.name
`,
      },
      language: {
        label: "Language",
        options: [
          { label: "Русский", value: "ru" },
          { label: "English", value: "en" },
        ],
      },
    },
  },
};


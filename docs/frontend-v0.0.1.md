# Tauri 2.0 + Vue + Tailwind CSS 项目初始化与前端搭建指南

## 一、环境准备与项目初始化

### 1. 前置条件检查

- 安装 Node.js ≥18.x（推荐使用 nvm 管理版本）
- 安装 Rust 工具链（通过 rustup）
- 安装必备工具：
  ```bash
  # 基础构建工具
  sudo apt install build-essential libwebkit2gtk-4.0-dev libssl-dev
  # Tauri CLI
  cargo install create-tauri-app
  ```

### 2. 项目创建

使用官方脚手架初始化：

```bash
npm create tauri-app@latest
```

选项配置：

```
✔ Project name: rag-web
✔ Choose your frontend framework: Vue
✔ Choose your UI styling: Tailwind CSS
✔ Choose TypeScript: Yes
✔ Choose code quality tools: ESLint
```

## 二、依赖安装与配置

### 1. 核心依赖

```bash
cd rag-web && npm install
# 补充常用依赖
npm install @tauri-apps/api @headlessui/vue heroicons/vue
```

### 2. Tailwind 配置验证

检查 `tailwind.config.js`：

```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    // 添加 Tauri 前端入口文件
    "./src-tauri/**/*.{html,rs}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

## 三、项目结构规划

### 1. 推荐目录结构

```
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 通用组件
│   ├── views/           # 页面视图
│   ├── stores/          # Pinia 状态管理
│   ├── utils/           # 工具函数
│   └── main.ts          # 入口文件
├── src-tauri/
│   ├── icons/           # 应用图标
│   ├── Cargo.toml       # Rust 依赖配置
│   └── tauri.conf.json  # Tauri 主配置
```

### 2. Tauri 配置调整

在 `tauri.conf.json` 中：

```json
{
  "build": {
    "distDir": "../dist",
    "devPath": "http://localhost:5173",
    "beforeBuildCommand": "npm run build"
  },
  "security": {
    "csp": "default-src 'self'"
  }
}
```

## 四、基础页面搭建

### 1. 主界面布局

`src/App.vue` 基础模板：

```vue
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <nav class="bg-white shadow-sm">
      <div class="mx-auto max-w-7xl px-4 py-3">
        <div class="flex items-center justify-between">
          <h1 class="text-xl font-bold text-gray-900">RAG 管理系统</h1>
          <div class="flex space-x-4">
            <button class="rounded-lg px-3 py-2 hover:bg-gray-100">
              文件上传
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 内容区域 -->
    <main class="mx-auto max-w-7xl px-4 py-6">
      <FileUploadSection />
    </main>
  </div>
</template>

<script setup>
import FileUploadSection from "./components/FileUploadSection.vue";
</script>
```

### 2. 核心组件开发

`src/components/FileUploadSection.vue`：

```vue
<template>
  <div class="rounded-lg border bg-white p-6 shadow">
    <h2 class="mb-4 text-lg font-semibold">文件上传</h2>
    <div
      class="flex h-32 items-center justify-center rounded border-2 border-dashed border-gray-300 hover:border-blue-500"
      @drop.prevent="handleDrop"
      @dragover.prevent
    >
      <input type="file" @change="handleSelect" hidden />
      <button
        @click="$refs.fileInput.click()"
        class="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
      >
        选择文件
      </button>
    </div>
  </div>
</template>

<script setup>
const handleDrop = (e) => {
  const files = e.dataTransfer.files;
  processFiles(files);
};

const handleSelect = (e) => {
  const files = e.target.files;
  processFiles(files);
};

const processFiles = async (files) => {
  // 调用 Tauri 文件处理 API
  const { invoke } = await import("@tauri-apps/api/tauri");
  try {
    const response = await invoke("process_file", {
      file: Array.from(files)[0],
    });
    console.log("处理结果:", response);
  } catch (error) {
    console.error("文件处理失败:", error);
  }
};
</script>
```

## 五、开发工作流

### 1. 启动开发环境

```bash
npm run tauri dev
# 同时启动：
# - Vite 前端开发服务器（5173 端口）
# - Tauri 桌面应用窗口

# 独立运行命令：
npm run dev    # 仅前端开发
npm run tauri dev -- --open # 自动打开应用窗口
```

### 2. 构建生产版本

```bash
npm run tauri build
# 输出结果：
# - 前端构建产物在 dist/
# - 可执行文件在 src-tauri/target/release/
```

## 六、最佳实践建议

### 1. 组件设计原则

- 原子化设计：按功能拆分为基础组件（Button/Input）和业务组件（FileUploader）
- 状态管理：简单场景使用 reactive + provide/inject，复杂场景采用 Pinia
- 样式规范：
  ```css
  /* 使用 Tailwind 自定义类 */
  @layer components {
    .card {
      @apply rounded-lg border bg-white p-6 shadow;
    }
  }
  ```

### 2. 性能优化

1. **代码分割**：

   ```javascript
   // 动态加载 Tauri API
   const { invoke } = await import("@tauri-apps/api/tauri");
   ```

2. **资源处理**：
   ```javascript
   // 在 vite.config.ts 中添加优化配置
   export default defineConfig({
     build: {
       assetsInlineLimit: 4096, // 4KB 以下文件转为 base64
     },
   });
   ```

## 七、注意事项

### 1. 安全限制处理

在 `tauri.conf.json` 中启用必要权限：

```json
{
  "tauri": {
    "allowlist": {
      "fs": {
        "scope": ["$DOCUMENT/**", "$DOWNLOAD/**"]
      }
    }
  }
}
```

### 2. 常见问题解决

1. **Rust 编译错误**：

   ```bash
   # 清理缓存
   cargo clean
   ```

2. **样式不生效**：
   ```bash
   # 重新生成 Tailwind CSS
   npx tailwindcss -i ./src/input.css -o ./src/output.css --watch
   ```

### 3. 调试工具

- Vue Devtools 集成：

  ```javascript
  // main.ts
  import { devtools } from "@vue/devtools";
  if (process.env.NODE_ENV === "development") {
    devtools.connect();
  }
  ```

- Tauri 日志查看：
  ```bash
  # 查看 Rust 日志
  TAURI_LOG=debug npm run tauri dev
  ```

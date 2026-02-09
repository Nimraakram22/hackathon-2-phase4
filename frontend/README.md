# Todo Chatbot Frontend

React frontend for the AI-powered todo chatbot, built with Vite, TypeScript, and OpenAI ChatKit.

## Features

- **ChatKit Integration**: Production-ready chat interface with streaming support
- **JWT Authentication**: Secure login and registration
- **Type Safety**: Full TypeScript support with strict mode
- **Modern React**: React 18 with hooks and functional components
- **Fast Development**: Vite for instant HMR and fast builds

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript (strict mode)
- **Chat UI**: OpenAI ChatKit React
- **HTTP Client**: Axios
- **Styling**: CSS

## Setup

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

1. **Install dependencies**:

```bash
npm install
```

2. **Configure environment variables**:

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Required environment variables:
- `VITE_API_URL`: Backend API URL (e.g., `http://localhost:8001`)
- `VITE_CHATKIT_URL`: ChatKit endpoint URL (e.g., `http://localhost:8001/chatkit`)
- `VITE_CHATKIT_DOMAIN_KEY`: ChatKit domain key (e.g., `local-dev`)

3. **Start development server**:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

## Development

### Running Tests

```bash
npm test
```

### Type Checking

```bash
npm run type-check
```

### Building for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── AuthProvider.tsx    # Authentication context
│   │   ├── Auth.tsx             # Login/register UI
│   │   └── ChatInterface.tsx   # ChatKit integration
│   ├── services/        # API client
│   │   └── api.ts
│   ├── App.tsx          # Root component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── package.json         # npm dependencies
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Usage

1. **Register**: Create a new account with email and password (min 8 characters)
2. **Login**: Sign in with your credentials
3. **Chat**: Start chatting with the AI assistant to manage your tasks

### Example Commands

- "Add a task to buy groceries"
- "Show me my tasks"
- "Mark task 1 as complete"
- "Update task 2 to 'Buy milk and eggs'"
- "Delete the groceries task"

## License

MIT

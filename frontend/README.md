# ArXiv Curator Frontend

A clean, modern Vue.js frontend for the ArXiv Curator application.

## 🚀 Features

- **Modern Vue 3** with Composition API
- **Vite** for lightning-fast development
- **Tailwind CSS** for beautiful, responsive design
- **Pinia** for state management
- **Vue Router** for navigation
- **Axios** for API communication

## 📦 Installation

```bash
cd frontend
npm install
```

## 🛠️ Development

```bash
# Start development server
npm run dev
```

The app will be available at http://localhost:3000

## 🏗️ Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Configuration

The frontend is configured to proxy API requests to the Flask backend running on port 5000.

To change the API endpoint, modify `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true
  }
}
```

## 📁 Project Structure

```
src/
├── components/       # Reusable Vue components
├── views/           # Page components
├── stores/          # Pinia stores
├── services/        # API service layer
├── router/          # Vue Router configuration
└── assets/          # Static assets and styles
```

## 🎨 Components

### Core Components
- `PaperCard.vue` - Displays paper summary card
- `ScoreBadge.vue` - Shows relevance score
- `StatsCard.vue` - Dashboard statistics
- `LoadingSpinner.vue` - Loading state indicator

### Views
- `HomePage.vue` - Dashboard with stats and recent papers
- `PapersView.vue` - Browse all papers with filters
- `PaperDetail.vue` - Full paper details and AI summary
- `AboutView.vue` - About the application

## 🔗 API Integration

The frontend expects these API endpoints:

- `GET /api/papers` - List papers with optional filters
- `GET /api/paper/:arxivId` - Get single paper details
- `GET /api/stats` - Get dashboard statistics

## 🚦 State Management

Using Pinia for state management:

```javascript
// Access papers store
import { usePapersStore } from '@/stores/papers'

const papersStore = usePapersStore()
await papersStore.fetchPapers()
```

## 📱 Responsive Design

The UI is fully responsive with breakpoints:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## 🔒 Future Enhancements

- [ ] User authentication
- [ ] Advanced search functionality
- [ ] Paper bookmarking
- [ ] Export functionality
- [ ] Dark mode support

import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles/candela.css';
import { StudioProvider, useStudio } from './context/StudioContext';
import { ActionsProvider } from './context/ActionsContext';
import { NotFoundView } from './app/views/NotFoundView';

// Split: the studio app never downloads the landing page's globe and videos, and the landing loads the app only once.
const LandingPage = React.lazy(() => import('./landing/LandingPage').then(m => ({ default: m.LandingPage })));
const AppShell = React.lazy(() => import('./app/AppShell').then(m => ({ default: m.AppShell })));
const FilmsGalleryPage = React.lazy(() => import('./public_pages/FilmsGalleryPage').then(m => ({ default: m.FilmsGalleryPage })));
const FilmPublicPage = React.lazy(() => import('./public_pages/FilmPublicPage').then(m => ({ default: m.FilmPublicPage })));
const HowItWorksPage = React.lazy(() => import('./public_pages/HowItWorksPage').then(m => ({ default: m.HowItWorksPage })));
const PricingPage = React.lazy(() => import('./public_pages/PricingPage').then(m => ({ default: m.PricingPage })));
const Loading: React.FC = () => <div style={{ position: 'fixed', inset: 0, display: 'grid', placeItems: 'center', color: 'var(--tx3)', fontSize: 13 }}>Loading…</div>;

const Router: React.FC = () => {
  const { currentPath } = useStudio();

  // /docs redirect
  if (currentPath === '/docs') {
    window.location.href = 'https://github.com/FranklinMburu/Autonomous-content-studio#readme';
    return null;
  }

  // App routes
  if (currentPath.startsWith('/app')) {
    return <AppShell />;
  }

  // Public film detail /films/:id
  if (currentPath.startsWith('/films/')) {
    const filmId = currentPath.replace('/films/', '');
    return <FilmPublicPage filmId={filmId} />;
  }

  // Public film gallery
  if (currentPath === '/films') {
    return <FilmsGalleryPage />;
  }

  // How it works standalone
  if (currentPath === '/how-it-works') {
    return <HowItWorksPage />;
  }

  // Pricing
  if (currentPath === '/pricing') {
    return <PricingPage />;
  }

  // Root landing page
  if (currentPath === '/' || currentPath === '') {
    return <LandingPage />;
  }

  // 404
  return <NotFoundView />;
};

const App: React.FC = () => {
  return (
    <StudioProvider>
      <ActionsProvider>
        <React.Suspense fallback={<Loading />}>
          <Router />
        </React.Suspense>
      </ActionsProvider>
    </StudioProvider>
  );
};

const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(<App />);
}

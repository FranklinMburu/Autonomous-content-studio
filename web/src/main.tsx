import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles/candela.css';
import { StudioProvider, useStudio } from './context/StudioContext';
import { LandingPage } from './landing/LandingPage';
import { AppShell } from './app/AppShell';
import { FilmsGalleryPage } from './public_pages/FilmsGalleryPage';
import { FilmPublicPage } from './public_pages/FilmPublicPage';
import { HowItWorksPage } from './public_pages/HowItWorksPage';
import { PricingPage } from './public_pages/PricingPage';
import { NotFoundView } from './app/views/NotFoundView';

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
      <Router />
    </StudioProvider>
  );
};

const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(<App />);
}

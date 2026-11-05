import React, { createContext, useContext, useEffect, useState, useMemo, useCallback } from 'react';
import { createStudio, DEFAULTS, StudioError } from '../lib/github-data.js';

export interface StudioContextValue {
  studio: ReturnType<typeof createStudio>;
  films: any[];
  runs: any[];
  topics: string[];
  reviewItems: any[];
  polishItems: any[];
  uploadItems: any[];
  uploadedItems: any[];
  alerts: any[];
  scheduleData: any;
  nextSlots: string[];
  modelsData: any;
  memorySeedData: any;
  labRunsData: any[];
  statusBoardData: any;
  loading: boolean;
  error: { kind: string; message: string } | null;
  theme: 'dark' | 'light' | 'system';
  setTheme: (t: 'dark' | 'light' | 'system') => void;
  activeChannel: string;
  setActiveChannel: (c: string) => void;
  refresh: () => Promise<void>;
  clearCache: () => void;
  navigate: (path: string) => void;
  currentPath: string;
}

const StudioContext = createContext<StudioContextValue | null>(null);

export const StudioProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [studio] = useState(() => createStudio());
  const [films, setFilms] = useState<any[]>([]);
  const [runs, setRuns] = useState<any[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [reviewItems, setReviewItems] = useState<any[]>([]);
  const [polishItems, setPolishItems] = useState<any[]>([]);
  const [uploadItems, setUploadItems] = useState<any[]>([]);
  const [uploadedItems, setUploadedItems] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [scheduleData, setScheduleData] = useState<any>(null);
  const [nextSlots, setNextSlots] = useState<string[]>([]);
  const [modelsData, setModelsData] = useState<any>(null);
  const [memorySeedData, setMemorySeedData] = useState<any>(null);
  const [labRunsData, setLabRunsData] = useState<any[]>([]);
  const [statusBoardData, setStatusBoardData] = useState<any>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ kind: string; message: string } | null>(null);
  const [activeChannel, setActiveChannel] = useState<string>('HR');
  const [theme, setThemeState] = useState<'dark' | 'light' | 'system'>(() => {
    return (localStorage.getItem('candela:theme') as 'dark' | 'light' | 'system') || 'dark';
  });

  const [currentPath, setCurrentPath] = useState<string>(() => window.location.pathname || '/');

  // Handle URL history navigation
  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname || '/');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = useCallback((path: string) => {
    if (window.location.pathname !== path) {
      window.history.pushState({}, '', path);
      setCurrentPath(path);
      window.scrollTo(0, 0);
    }
  }, []);

  // Theme application
  const setTheme = useCallback((t: 'dark' | 'light' | 'system') => {
    setThemeState(t);
    localStorage.setItem('candela:theme', t);
  }, []);

  useEffect(() => {
    const applyTheme = () => {
      const isLight =
        theme === 'light' ||
        (theme === 'system' && window.matchMedia('(prefers-color-scheme: light)').matches);
      if (isLight) {
        document.body.classList.add('light');
      } else {
        document.body.classList.remove('light');
      }
    };
    applyTheme();

    if (theme === 'system') {
      const mq = window.matchMedia('(prefers-color-scheme: light)');
      mq.addEventListener('change', applyTheme);
      return () => mq.removeEventListener('change', applyTheme);
    }
  }, [theme]);

  // Load data
  const loadData = useCallback(async () => {
    try {
      setError(null);
      // Fetch in parallel with soft fallback
      const pFilms = studio.films().catch(e => {
        if (e instanceof StudioError) setError({ kind: e.kind, message: e.message });
        return [];
      });
      const pRuns = studio.runs(30).catch(() => []);
      const pTopics = studio.topics().catch(() => []);
      const pRev = studio.reviewQueue().catch(() => []);
      const pPol = studio.polishQueue().catch(() => []);
      const pUp = studio.uploadQueue().catch(() => []);
      const pUped = studio.uploaded().catch(() => []);
      const pAlerts = studio.alerts().catch(() => []);
      const pSched = studio.schedule().catch(() => null);
      const pModels = studio.models().catch(() => null);
      const pMem = studio.memorySeed().catch(() => null);
      const pLab = studio.labRuns().catch(() => []);
      const pStatus = studio.statusBoard().catch(() => null);

      const [
        rFilms,
        rRuns,
        rTopics,
        rRev,
        rPol,
        rUp,
        rUped,
        rAlerts,
        rSched,
        rModels,
        rMem,
        rLab,
        rStatus,
      ] = await Promise.all([
        pFilms,
        pRuns,
        pTopics,
        pRev,
        pPol,
        pUp,
        pUped,
        pAlerts,
        pSched,
        pModels,
        pMem,
        pLab,
        pStatus,
      ]);

      setFilms(rFilms);
      setRuns(rRuns);
      setTopics(rTopics);
      setReviewItems(rRev);
      setPolishItems(rPol);
      setUploadItems(rUp);
      setUploadedItems(rUped);
      setAlerts(rAlerts);
      setScheduleData(rSched);
      if (rSched && rSched.utc) {
        const rawSlots = studio.nextSlots(rSched.utc, 15);
        const formatted = rawSlots.map((d: any) => {
          if (d instanceof Date) {
            return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
          }
          return String(d || '');
        });
        setNextSlots(formatted);
      }
      setModelsData(rModels);
      setMemorySeedData(rMem);
      setLabRunsData(rLab);
      setStatusBoardData(rStatus);
    } catch (err: any) {
      setError({ kind: err?.kind || 'network', message: err?.message || 'Could not reach GitHub' });
    } finally {
      setLoading(false);
    }
  }, [studio]);

  useEffect(() => {
    loadData();
    // Live refresh of runs every 30s while document is visible
    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        studio.runs(30).then(setRuns).catch(() => {});
      }
    }, 30000);
    return () => clearInterval(timer);
  }, [loadData, studio]);

  const clearCache = useCallback(() => {
    try {
      sessionStorage.clear();
    } catch {
      // ignore
    }
    loadData();
  }, [loadData]);

  const value = useMemo(
    () => ({
      studio,
      films,
      runs,
      topics,
      reviewItems,
      polishItems,
      uploadItems,
      uploadedItems,
      alerts,
      scheduleData,
      nextSlots,
      modelsData,
      memorySeedData,
      labRunsData,
      statusBoardData,
      loading,
      error,
      theme,
      setTheme,
      activeChannel,
      setActiveChannel,
      refresh: loadData,
      clearCache,
      navigate,
      currentPath,
    }),
    [
      studio,
      films,
      runs,
      topics,
      reviewItems,
      polishItems,
      uploadItems,
      uploadedItems,
      alerts,
      scheduleData,
      nextSlots,
      modelsData,
      memorySeedData,
      labRunsData,
      statusBoardData,
      loading,
      error,
      theme,
      setTheme,
      activeChannel,
      setActiveChannel,
      loadData,
      clearCache,
      navigate,
      currentPath,
    ]
  );

  return <StudioContext.Provider value={value}>{children}</StudioContext.Provider>;
};

export const useStudio = () => {
  const ctx = useContext(StudioContext);
  if (!ctx) throw new Error('useStudio must be used within a StudioProvider');
  return ctx;
};

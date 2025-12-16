/**
 * i18n utility functions for Data.mn
 */

import { ui, defaultLang, type Language } from './ui';

/**
 * Get a translated string for the given key and language
 */
export function t(lang: Language, key: keyof typeof ui.en): string {
  return ui[lang][key] || ui[defaultLang][key] || key;
}

/**
 * Get the language from a URL path
 * Returns the language code if found, otherwise returns default language
 */
export function getLangFromUrl(url: URL): Language {
  const [, lang] = url.pathname.split('/');
  if (lang in ui) {
    return lang as Language;
  }
  return defaultLang;
}

/**
 * Get the path without the language prefix
 */
export function getPathWithoutLang(pathname: string): string {
  const parts = pathname.split('/').filter(Boolean);
  if (parts[0] === 'en' || parts[0] === 'mn') {
    return '/' + parts.slice(1).join('/');
  }
  return pathname;
}

/**
 * Create a localized path
 */
export function localizedPath(lang: Language, path: string): string {
  // Remove any existing language prefix
  const cleanPath = getPathWithoutLang(path);
  // Add the new language prefix, avoiding trailing slash for root
  if (cleanPath === '/' || cleanPath === '') {
    return `/${lang}`;
  }
  return `/${lang}${cleanPath}`;
}

/**
 * Get the alternate language
 */
export function getAlternateLang(lang: Language): Language {
  return lang === 'en' ? 'mn' : 'en';
}

/**
 * Create a translation function bound to a specific language
 * Useful in components: const t = useTranslations(lang);
 */
export function useTranslations(lang: Language) {
  return function translate(key: keyof typeof ui.en): string {
    return t(lang, key);
  };
}

/**
 * Format a number according to locale
 */
export function formatNumber(num: number, lang: Language): string {
  const locale = lang === 'mn' ? 'mn-MN' : 'en-US';
  return new Intl.NumberFormat(locale).format(num);
}

/**
 * Format a date according to locale
 */
export function formatDate(date: Date, lang: Language): string {
  const locale = lang === 'mn' ? 'mn-MN' : 'en-US';
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
}

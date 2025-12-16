/**
 * i18n module for Data.mn
 *
 * Usage in Astro components:
 *
 * import { getLangFromUrl, useTranslations } from '~/i18n';
 *
 * const lang = getLangFromUrl(Astro.url);
 * const t = useTranslations(lang);
 *
 * <h1>{t('home.hero.title')}</h1>
 */

export { languages, defaultLang, ui, type Language } from './ui';
export {
  t,
  getLangFromUrl,
  getPathWithoutLang,
  localizedPath,
  getAlternateLang,
  useTranslations,
  formatNumber,
  formatDate,
} from './utils';

import { getPermalink, getBlogPermalink, getAsset } from './utils/permalinks';

export const headerData = {
  links: [
    {
      text: 'Data',
      href: getPermalink('/data'),
    },
    {
      text: 'Reports',
      href: getPermalink('/reports'),
    },
    {
      text: 'Insights',
      href: getPermalink('/insights'),
    },
    {
      text: 'About',
      href: getPermalink('/about'),
    },
  ],
  actions: [{ text: 'Search', href: '/search', icon: 'tabler:search' }],
};

export const footerData = {
  links: [
    {
      title: 'Content',
      links: [
        { text: 'Data', href: '/data' },
        { text: 'Reports', href: '/reports' },
        { text: 'Insights', href: '/insights' },
        { text: 'Search', href: '/search' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { text: 'About', href: '/about' },
        { text: 'Contact', href: '/mn/contact' },
        { text: 'Terms', href: '/terms' },
        { text: 'Privacy', href: '/privacy' },
      ],
    },
  ],
  secondaryLinks: [],
  socialLinks: [
    { ariaLabel: 'X', icon: 'tabler:brand-x', href: '#' },
    { ariaLabel: 'RSS', icon: 'tabler:rss', href: getAsset('/rss.xml') },
  ],
  footNote: `
    Data.mn · All rights reserved.
  `,
};

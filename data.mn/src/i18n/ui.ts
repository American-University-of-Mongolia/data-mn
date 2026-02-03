/**
 * UI translations for Data.mn
 *
 * Add all translatable UI strings here.
 * Structure: ui[language][key] = "translated string"
 */

export const languages = {
  en: 'English',
  mn: 'Монгол',
} as const;

export const defaultLang = 'mn' as const;

export type Language = keyof typeof languages;

export const ui = {
  en: {
    // Site
    'site.name': 'Data.mn',
    'site.tagline': 'Statistics & Insights for Mongolia',
    'site.description': 'Your source for reliable data, interactive visualizations, and in-depth analysis',

    // Navigation
    'nav.data': 'Data',
    'nav.reports': 'Reports',
    'nav.insights': 'Insights',
    'nav.about': 'About',
    'nav.search': 'Search',

    // Homepage
    'home.hero.title': "Mongolia's data, all in one place",
    'home.hero.subtitle': '',
    'home.popular': 'Popular:',
    'home.keyIndicators': 'Key Indicators',
    'home.trendingData': 'Latest Data',
    'home.viewAllData': 'View all data',
    'home.exploreByTopic': 'Explore by Topic',
    // 'home.browseCategories': 'Browse our most popular categories',
    'home.featuredReports': 'Featured Reports',
    'home.viewAllReports': 'View all reports',
    'home.latestInsights': 'Latest Insights',
    'home.insightsDescription': 'Stay informed with our latest analysis, trends, and commentary on data and statistics',
    'home.viewAllInsights': 'View all insights',

    // Open Data Stats
    'stats.population': 'Population',
    'stats.inflation': 'Inflation rate',
    'stats.unemployment': 'Unemployment rate',
    'stats.laborForce': 'Labor force participation',
    'stats.gdp': 'Gross Domestic Product',
    'stats.livestock': 'Livestock count',
    'stats.salary': 'Average salary',
    'stats.householdIncome': 'Average household income',
    'stats.trade': 'Foreign trade',

    // Units
    'unit.percent': '%',
    'unit.billion': ' billion',
    'unit.billionUSD': ' billion USD',
    'unit.trillion': ' trillion',
    'unit.trillionMNT': ' trillion ₮',
    'unit.million': ' million',
    'unit.millionMNT': ' million ₮',

    // Search
    'search.placeholder': 'Search datasets, reports, and insights...',
    'search.title': 'Search',
    'search.results': 'results',
    'search.noResults': 'No results found',
    'search.tryDifferent': 'Try a different search term',

    // Content types
    'type.data': 'Data',
    'type.report': 'Report',
    'type.insight': 'Insight',

    // Common
    'common.readMore': 'Read more',
    'common.download': 'Download',
    'common.share': 'Share',
    'common.category': 'Category',
    'common.tags': 'Tags',
    'common.publishedOn': 'Published on',
    'common.updatedOn': 'Updated on',
    'common.author': 'Author',
    'common.version': 'Version',

    // About
    'about.title': 'About Us',

    // Contact
    'contact.title': 'Contact',
    'contact.heading': 'Get in Touch',
    'contact.description': 'For data inquiries, partnership opportunities, or feedback — we\'d love to hear from you.',
    'contact.emailLabel': 'Email us at',
    'contact.responseTime': 'We typically respond within 1-2 business days.',

    // Footer
    'footer.content': 'Content',
    'footer.resources': 'Resources',
    'footer.categories': 'Categories',
    'footer.contact': 'Contact',
    'footer.terms': 'Terms',
    'footer.privacy': 'Privacy',
    'footer.changelog': 'Changelog',
    'footer.allRightsReserved': 'All rights reserved',

    // Topics
    'topic.mongolia': 'Mongolia',
    'topic.demographics': 'Demographics',
    'topic.economy': 'Economy',
    'topic.mining': 'Mining',
    'topic.education': 'Education',
    'topic.healthcare': 'Healthcare',
    'topic.trade': 'Trade',
    'topic.energy': 'Energy',
    'topic.tourism': 'Tourism',
    'topic.urbanization': 'Urbanization',

    // Deprecation notices (URL stability)
    'deprecated.notice': 'This dataset has been deprecated',
    'deprecated.reason': 'Reason',
    'deprecated.replacement': 'View the updated data',
    'deprecated.asOf': 'Deprecated on',

    // Changelog
    'changelog.title': 'Changelog',
    'changelog.description': 'Track additions, updates, and changes to our dataset collection',
    'changelog.action.added': 'Added',
    'changelog.action.updated': 'Updated',
    'changelog.action.removed': 'Removed',
    'changelog.noChanges': 'No changes recorded yet',
    'changelog.viewDataset': 'View dataset',
  },
  mn: {
    // Site
    'site.name': 'Data.mn',
    'site.tagline': 'Монголын статистик ба шинжилгээ',
    'site.description': 'Найдвартай өгөгдөл, интерактив дүрслэл, гүнзгий шинжилгээний эх сурвалж',

    // Navigation
    'nav.data': 'Өгөгдөл',
    'nav.reports': 'Тайлан',
    'nav.insights': 'Нийтлэл',
    'nav.about': 'Тухай',
    'nav.search': 'Хайлт',

    // Homepage
    'home.hero.title': 'Монголын бүх датаг нэг дороос',
    'home.hero.subtitle': '',
    'home.popular': 'Түгээмэл:',
    'home.keyIndicators': 'Гол үзүүлэлтүүд',
    'home.trendingData': 'Шинэ өгөгдөл',
    'home.viewAllData': 'Бүх өгөгдөл үзэх',
    'home.exploreByTopic': 'Сэдвээр ангилан судлах',
    // 'home.browseCategories': 'Хамгийн алдартай ангиллуудыг үзэх',
    'home.featuredReports': 'Онцлох тайлангууд',
    'home.viewAllReports': 'Бүх тайлан үзэх',
    'home.latestInsights': 'Сүүлийн нийтлэлүүд',
    'home.insightsDescription': 'Өгөгдөл, статистикийн талаарх хамгийн сүүлийн шинжилгээ, чиг хандлагатай танилцаарай',
    'home.viewAllInsights': 'Бүх нийтлэл үзэх',

    // Open Data Stats
    'stats.population': 'Хүн ам',
    'stats.inflation': 'Инфляцийн түвшин',
    'stats.unemployment': 'Ажилгүйдлийн түвшин',
    'stats.laborForce': 'Хөдөлмөрийн оролцоо',
    'stats.gdp': 'Дотоодын нийт бүтээгдэхүүн',
    'stats.livestock': 'Малын тоо толгой',
    'stats.salary': 'Дундаж цалин',
    'stats.householdIncome': 'Өрхийн дундаж орлого',
    'stats.trade': 'Гадаад худалдаа',

    // Units
    'unit.percent': '%',
    'unit.billion': ' тэрбум',
    'unit.billionUSD': ' тэрбум ам.доллар',
    'unit.trillion': ' их наяд',
    'unit.trillionMNT': ' их наяд ₮',
    'unit.million': ' сая',
    'unit.millionMNT': ' сая ₮',

    // Search
    'search.placeholder': 'Өгөгдөл, тайлан, нийтлэлээс хайх...',
    'search.title': 'Хайлт',
    'search.results': 'үр дүн',
    'search.noResults': 'Үр дүн олдсонгүй',
    'search.tryDifferent': 'Өөр түлхүүр үгээр хайна уу',

    // Content types
    'type.data': 'Өгөгдөл',
    'type.report': 'Тайлан',
    'type.insight': 'Нийтлэл',

    // Common
    'common.readMore': 'Дэлгэрэнгүй',
    'common.download': 'Татах',
    'common.share': 'Хуваалцах',
    'common.category': 'Ангилал',
    'common.tags': 'Шошго',
    'common.publishedOn': 'Нийтэлсэн',
    'common.updatedOn': 'Шинэчилсэн',
    'common.author': 'Зохиогч',
    'common.version': 'Хувилбар',

    // About
    'about.title': 'Бидний тухай',

    // Contact
    'contact.title': 'Холбоо барих',
    'contact.heading': 'Холбоо барих',
    'contact.description': 'Өгөгдлийн асуулт, хамтын ажиллагааны санал, эсвэл санал хүсэлт байвал бидэнтэй холбогдоорой.',
    'contact.emailLabel': 'Имэйл хаяг',
    'contact.responseTime': 'Бид ихэвчлэн 1-2 ажлын өдрийн дотор хариу өгдөг.',

    // Footer
    'footer.content': 'Агуулга',
    'footer.resources': 'Нөөц',
    'footer.categories': 'Ангилал',
    'footer.contact': 'Холбоо барих',
    'footer.terms': 'Нөхцөл',
    'footer.privacy': 'Нууцлал',
    'footer.changelog': 'Өөрчлөлт',
    'footer.allRightsReserved': 'Бүх эрх хуулиар хамгаалагдсан',

    // Topics
    'topic.mongolia': 'Монгол',
    'topic.demographics': 'Хүн ам зүй',
    'topic.economy': 'Эдийн засаг',
    'topic.mining': 'Уул уурхай',
    'topic.education': 'Боловсрол',
    'topic.healthcare': 'Эрүүл мэнд',
    'topic.trade': 'Худалдаа',
    'topic.energy': 'Эрчим хүч',
    'topic.tourism': 'Аялал жуулчлал',
    'topic.urbanization': 'Хот суурьшил',

    // Deprecation notices (URL stability)
    'deprecated.notice': 'Энэ өгөгдлийн багц хуучирсан',
    'deprecated.reason': 'Шалтгаан',
    'deprecated.replacement': 'Шинэчилсэн өгөгдлийг үзэх',
    'deprecated.asOf': 'Хуучирсан огноо',

    // Changelog
    'changelog.title': 'Өөрчлөлтийн түүх',
    'changelog.description': 'Өгөгдлийн багцын нэмэлт, шинэчлэлт, өөрчлөлтүүдийг хянах',
    'changelog.action.added': 'Нэмсэн',
    'changelog.action.updated': 'Шинэчилсэн',
    'changelog.action.removed': 'Устгасан',
    'changelog.noChanges': 'Өөрчлөлт бүртгэгдээгүй байна',
    'changelog.viewDataset': 'Өгөгдөл үзэх',
  },
} as const;

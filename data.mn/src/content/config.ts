import { z, defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const metadataDefinition = () =>
  z
    .object({
      title: z.string().optional(),
      ignoreTitleTemplate: z.boolean().optional(),

      canonical: z.string().url().optional(),

      robots: z
        .object({
          index: z.boolean().optional(),
          follow: z.boolean().optional(),
        })
        .optional(),

      description: z.string().optional(),

      openGraph: z
        .object({
          url: z.string().optional(),
          siteName: z.string().optional(),
          images: z
            .array(
              z.object({
                url: z.string(),
                width: z.number().optional(),
                height: z.number().optional(),
              })
            )
            .optional(),
          locale: z.string().optional(),
          type: z.string().optional(),
        })
        .optional(),

      twitter: z
        .object({
          handle: z.string().optional(),
          site: z.string().optional(),
          cardType: z.string().optional(),
        })
        .optional(),
    })
    .optional();

// Base schema for all content types
const baseSchema = z.object({
  publishDate: z.date().optional(),
  updateDate: z.date().optional(),
  draft: z.boolean().optional(),

  title: z.string(),
  excerpt: z.string().optional(),
  image: z.string().optional(),

  author: z.string().optional(),
  keywords: z.array(z.string()).optional(), // For search functionality
  tags: z.array(z.string()).optional(),

  metadata: metadataDefinition(),
});

// Data pages collection - for statistical data pages with charts
// Files organized by language: src/data/data/en/*.mdx, src/data/data/mn/*.mdx
// IDs will be: en/filename, mn/filename
const dataCollection = defineCollection({
  loader: glob({ pattern: ['**/*.md', '**/*.mdx'], base: 'src/data/data' }),
  schema: baseSchema.extend({
    category: z.string().optional(),

    // Data versioning fields
    dataVersion: z.number().optional(),
    dataDate: z.date().optional(),

    // Data files for download
    dataFiles: z.array(z.object({
      path: z.string(),
      format: z.string(), // csv, xlsx, json, etc.
      size: z.string().optional(),
      description: z.string().optional(),
    })).optional(),

    // Source attribution
    source: z.object({
      name: z.string(),
      url: z.string().url(),
      tableId: z.string().optional(),
    }).optional(),

    // Previous versions for reference
    previousVersions: z.array(z.object({
      version: z.number(),
      date: z.date(),
      path: z.string().optional(),
    })).optional(),
  }),
});

// Reports collection - for longer-form analytical reports
// Files organized by language: src/data/reports/en/*.mdx, src/data/reports/mn/*.mdx
const reportsCollection = defineCollection({
  loader: glob({ pattern: ['**/*.md', '**/*.mdx'], base: 'src/data/reports' }),
  schema: baseSchema.extend({
    reportType: z.string().optional(),
    category: z.string().optional(),
  }),
});

// Insights collection - for blog-style insights and analysis
// Files organized by language: src/data/insights/en/*.mdx, src/data/insights/mn/*.mdx
const insightsCollection = defineCollection({
  loader: glob({ pattern: ['**/*.md', '**/*.mdx'], base: 'src/data/insights' }),
  schema: baseSchema.extend({
    category: z.string().optional(),
  }),
});

// Changelog collection - tracks dataset additions, updates, and removals
// Files organized by language: src/data/changelog/en/*.mdx, src/data/changelog/mn/*.mdx
const changelogCollection = defineCollection({
  loader: glob({ pattern: ['**/*.md', '**/*.mdx'], base: 'src/data/changelog' }),
  schema: z.object({
    date: z.date(),
    action: z.enum(['added', 'updated', 'removed']),
    dataset_id: z.string(),
    dataset_name_en: z.string(),
    dataset_name_mn: z.string(),
    description_en: z.string(),
    description_mn: z.string(),
    source: z.string().optional(),
    version: z.number().optional(),
  }),
});

// Keep the original post collection for compatibility
const postCollection = defineCollection({
  loader: glob({ pattern: ['*.md', '*.mdx'], base: 'src/data/post' }),
  schema: z.object({
    publishDate: z.date().optional(),
    updateDate: z.date().optional(),
    draft: z.boolean().optional(),

    title: z.string(),
    excerpt: z.string().optional(),
    image: z.string().optional(),

    category: z.string().optional(),
    tags: z.array(z.string()).optional(),
    author: z.string().optional(),

    metadata: metadataDefinition(),
  }),
});

export const collections = {
  post: postCollection,
  data: dataCollection,
  reports: reportsCollection,
  insights: insightsCollection,
  changelog: changelogCollection,
};

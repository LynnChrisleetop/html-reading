# HTML Reading Library

A collection of self-contained HTML reading projects for books and long-form study materials.

Each title lives in its own subdirectory and may include:

- a standalone HTML reader;
- bilingual alignment or reading data;
- local notes and highlighting support;
- backup and export instructions;
- optional build or validation utilities.

Open the book-specific `README.md` inside each directory for usage notes and limitations. Personal credentials, browser databases, and other private runtime data must never be committed.

## Books

- [Thinking, Fast and Slow — Bilingual Reading Edition](books/快思慢想-双语阅读/README.md)
- [Oxford Phonics World 3 — Offline Reading and Audio App](books/牛津自然拼读/README.md)

The current Thinking, Fast and Slow artifact is the first-chapter bilingual sample prepared so far, not a complete transcription of the whole book.

The Oxford Phonics World 3 directory is a self-contained local reader bundle. It includes the reader source, rendered page images, book data, PDF, and local audio assets. After cloning, install Node.js 18 or newer and start it with the book directory's `start.cmd`.

## Copyright and access

Some book PDFs, scans, and audio recordings may be copyrighted. Before making this repository public, verify that you have permission to redistribute the bundled materials. If not, keep the repository private or commit only the reader code and your own data.

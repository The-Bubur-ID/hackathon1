Findings

- High – `SETUP_GUIDE.md:26-29`: Dokumen membagikan `DATABASE_URL` lengkap beserta username, password, host, dan port. Ini kredensial database nyata (atau terlihat nyata) yang sekarang tersimpan di repo. Segera ganti dengan placeholder dan rotasi password di Railway.
- High – `SETUP_GUIDE.md:62-70`: Contoh perintah ekspor juga menyertakan `DATABASE_URL` yang sama plus API key OpenAI berbentuk penuh. Ini melanggar praktik keamanan dan akan dianggap kebocoran secret. Ganti dengan placeholder yang jelas (`YOUR_DATABASE_URL`, `YOUR_OPENAI_KEY`) dan hapus nilai sensitif dari histori bila perlu.

Catatan

- Instruksi teknis lainnya di langkah 1–2 sudah tepat. Setelah mengganti secret dengan placeholder dan memastikan kredensial sudah diputar, dokumen siap dibagikan.***

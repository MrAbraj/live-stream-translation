# Streamify – Next-Gen Live Streaming Platform

**Streamify** is a real-time live streaming platform built for modern webinars, global training, and collaborative online experiences. It offers ultra-low latency streaming, interactive screen share translation, and dynamic media mixing—all powered by smart rendering and AI enhancements.

---

## 🚀 Key Features

- **Ultra-Low Latency Streaming**
  - Achieves ~400ms latency using LL-HLS with CEF-based pixel capture
- **AI-Powered Screen Share Translation**
  - Real-time translation of screen-shared content into local languages
  - Allows text selection and clickable links from the translated stream
- **Custom Stream Mixing Pipeline**
  - Mix camera, screen, and audio sources into a unified output
  - Rendered using Chromium Embedded Framework (CEF)
- **Interactive Slide Sharing**
  - Supports synced presenter tools like laser pointer and drawing
  - Slides translated per viewer’s local language for accessibility

---

## 🛠️ Tech Stack

- **Media Server:** [MediaMTX](https://github.com/bluenviron/mediamtx)
- **Rendering & Mixing:** Chromium Embedded Framework (CEF)
- **Text Detection:** [CRAFT (Character Region Awareness for Text Detection)](https://github.com/clovaai/CRAFT-pytorch)
- **Image Processing:** OpenCV
- **Translation API:** Google Cloud Translation
- **Streaming Protocol:** LL-HLS (Low-Latency HTTP Live Streaming)
- **Frontend:** HTML5, JavaScript, Custom Video Container

## 🌍 Ideal For

- Large webinars and virtual events
- International product launches
- Multilingual corporate trainings
- Real-time interactive demos and courses

---

## 🤝 Contributing

We welcome contributions to enhance translation accuracy, lower latency further, or extend media formats. Open an issue or pull request to get started!

---

## 📄 License

MIT License

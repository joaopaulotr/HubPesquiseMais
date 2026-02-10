<template>
  <div class="container">
    <header class="header">
      <h1>🎯 Pesquise+Hub</h1>
      <p>Transcrição de áudio e análise completa de vídeo com IA</p>
    </header>

    <div class="products-grid">
      <AudioTranscription />
      <VideoDescription />
    </div>
  </div>
</template>

<script>
import AudioTranscription from './components/AudioTranscription.vue'
import VideoDescription from './components/VideoDescription.vue'

export default {
  name: 'App',
  components: {
    AudioTranscription,
    VideoDescription
  }
}
</script>

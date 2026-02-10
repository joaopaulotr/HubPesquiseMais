<template>
  <div class="product-card">
    <h2 class="product-title">🎵 Áudio → Texto</h2>
    <p class="product-subtitle">Transcreva áudio em texto com timestamps</p>

    <div v-if="!file && !loading && !result">
      <div 
        class="upload-area"
        :class="{ 'dragover': isDragging }"
        @click="triggerFileInput"
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
      >
        <div class="upload-icon">🎤</div>
        <p><strong>Clique ou arraste</strong> um arquivo de áudio</p>
        <p style="font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem;">
          MP3, WAV, M4A, OGG, FLAC, AAC
        </p>
      </div>
      <input 
        ref="fileInput"
        type="file" 
        class="file-input"
        accept=".mp3,.wav,.m4a,.ogg,.flac,.aac"
        @change="handleFileSelect"
      />
    </div>

    <div v-if="file && !loading && !result" class="file-info">
      <div>
        <strong>{{ file.name }}</strong>
        <p style="font-size: 0.875rem; color: #6b7280;">
          {{ formatFileSize(file.size) }}
        </p>
      </div>
      <button class="btn btn-remove" @click="removeFile">Remover</button>
    </div>

    <button 
      v-if="file && !loading && !result"
      class="btn btn-primary"
      @click="transcribeAudio"
      :disabled="loading"
    >
      Transcrever Áudio
    </button>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Transcrevendo áudio... Isso pode levar alguns minutos.</p>
    </div>

    <div v-if="result" class="result">
      <h3>✅ Transcrição Concluída!</h3>
      
      <div class="result-content">
        {{ result.text }}
      </div>

      <div style="margin-bottom: 1rem;">
        <p><strong>Idioma detectado:</strong> {{ result.language }}</p>
        <p><strong>Segmentos:</strong> {{ result.segments_count }}</p>
      </div>

      <div class="result-files">
        <a 
          :href="getFileUrl(result.files.txt)" 
          target="_blank"
          class="file-link"
        >
          📄 Baixar TXT
        </a>
        <a 
          :href="getFileUrl(result.files.srt)" 
          target="_blank"
          class="file-link"
        >
          📝 Baixar SRT
        </a>
      </div>

      <button 
        class="btn btn-primary" 
        style="margin-top: 1rem;"
        @click="reset"
      >
        Nova Transcrição
      </button>
    </div>

    <div v-if="error" class="error">
      <strong>❌ Erro:</strong> {{ error }}
      <button 
        class="btn btn-primary" 
        style="margin-top: 1rem;"
        @click="reset"
      >
        Tentar Novamente
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AudioTranscription',
  data() {
    return {
      file: null,
      loading: false,
      result: null,
      error: null,
      isDragging: false,
      apiUrl: 'http://localhost:8000'
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.file = file
      }
    },
    handleDrop(event) {
      this.isDragging = false
      const file = event.dataTransfer.files[0]
      if (file) {
        this.file = file
      }
    },
    removeFile() {
      this.file = null
      this.$refs.fileInput.value = ''
    },
    async transcribeAudio() {
      this.loading = true
      this.error = null

      const formData = new FormData()
      formData.append('file', this.file)

      try {
        const response = await axios.post(
          `${this.apiUrl}/audio/transcribe`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        )

        this.result = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Erro ao processar áudio'
      } finally {
        this.loading = false
      }
    },
    getFileUrl(path) {
      return `${this.apiUrl}${path}`
    },
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    },
    reset() {
      this.file = null
      this.result = null
      this.error = null
      this.loading = false
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    }
  }
}
</script>

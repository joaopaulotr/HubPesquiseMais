<template>
  <div class="product-card">
    <h2 class="product-title">🎬 Vídeo → Descrição</h2>
    <p class="product-subtitle">Análise completa: visual + áudio com IA</p>

    <div v-if="!file && !loading && !result">
      <div 
        class="upload-area"
        :class="{ 'dragover': isDragging }"
        @click="triggerFileInput"
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
      >
        <div class="upload-icon">🎥</div>
        <p><strong>Clique ou arraste</strong> um arquivo de vídeo</p>
        <p style="font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem;">
          MP4, AVI, MOV, MKV, WEBM, FLV
        </p>
      </div>
      <input 
        ref="fileInput"
        type="file" 
        class="file-input"
        accept=".mp4,.avi,.mov,.mkv,.webm,.flv"
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
      @click="generateDescription"
      :disabled="loading"
    >
      Gerar Descrição
    </button>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Analisando vídeo completo... Isso pode levar alguns minutos.</p>
      <p style="font-size: 0.875rem; color: #6b7280;">
        Extraindo áudio → Transcrevendo → Analisando frames → Gerando descrição
      </p>
    </div>

    <div v-if="result" class="result">
      <h3>✅ Análise Concluída!</h3>
      
      <div>
        <h4 style="margin-bottom: 0.5rem;">📝 Descrição Completa:</h4>
        <div class="result-content">
          {{ result.description }}
        </div>
      </div>

      <div style="margin-top: 1rem;">
        <h4 style="margin-bottom: 0.5rem;">📄 Transcrição do Áudio:</h4>
        <div class="result-content" style="max-height: 200px;">
          {{ result.transcription }}
        </div>
      </div>

      <div style="margin: 1rem 0;">
        <p><strong>Idioma:</strong> {{ result.language }}</p>
        <p><strong>Frames analisados:</strong> {{ result.frames_analyzed }}</p>
      </div>

      <div class="result-files">
        <a 
          :href="getFileUrl(result.file)" 
          target="_blank"
          class="file-link"
        >
          📥 Baixar Resultado Completo
        </a>
      </div>

      <button 
        class="btn btn-primary" 
        style="margin-top: 1rem;"
        @click="reset"
      >
        Novo Vídeo
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
  name: 'VideoDescription',
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
    async generateDescription() {
      this.loading = true
      this.error = null

      const formData = new FormData()
      formData.append('file', this.file)

      try {
        const response = await axios.post(
          `${this.apiUrl}/video/description`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 300000 // 5 minutos de timeout
          }
        )

        this.result = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Erro ao processar vídeo'
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

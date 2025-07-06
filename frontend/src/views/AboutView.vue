<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">About ArXiv Curator</h1>
    
    <div class="prose prose-lg max-w-none">
      <div class="bg-white rounded-lg shadow p-8 mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">What is ArXiv Curator?</h2>
        <p class="text-gray-700 mb-4">
          ArXiv Curator is an AI-powered tool that automatically discovers, curates, and summarizes 
          research papers from ArXiv. It helps researchers and students stay up-to-date with the 
          latest developments in AI, Machine Learning, and Computer Science.
        </p>
        <p class="text-gray-700">
          Using advanced language models, we generate concise summaries and extract key points 
          from each paper, making it easier to quickly understand the main contributions without 
          reading the entire document.
        </p>
      </div>
      
      <div class="bg-white rounded-lg shadow p-8 mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">How It Works</h2>
        <ol class="list-decimal list-inside space-y-3 text-gray-700">
          <li>
            <strong>Paper Discovery:</strong> We regularly fetch recent papers from ArXiv based on 
            configured categories and keywords.
          </li>
          <li>
            <strong>Relevance Scoring:</strong> Each paper is scored based on its relevance to 
            current research trends and specified interests.
          </li>
          <li>
            <strong>AI Summarization:</strong> High-scoring papers are processed through advanced 
            language models to generate summaries and extract key points.
          </li>
          <li>
            <strong>Easy Browsing:</strong> Papers are presented in a clean, searchable interface 
            with filters for date, score, and categories.
          </li>
        </ol>
      </div>
      
      <div class="bg-white rounded-lg shadow p-8 mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Current Configuration</h2>
        <div class="space-y-2 text-gray-700">
          <p>
            <strong>Categories:</strong> cs.CL, cs.AI, cs.LG
          </p>
          <p>
            <strong>Keywords:</strong> LLM, language model, transformer, GPT, BERT
          </p>
          <p>
            <strong>AI Model:</strong> HuggingFace BART for summarization
          </p>
          <p>
            <strong>Update Frequency:</strong> Daily
          </p>
        </div>
      </div>
      
      <div class="bg-indigo-50 rounded-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Future Enhancements</h2>
        <ul class="list-disc list-inside space-y-2 text-gray-700">
          <li>User accounts with personalized recommendations</li>
          <li>Custom category and keyword configurations</li>
          <li>Email notifications for high-scoring papers</li>
          <li>Integration with reference managers</li>
          <li>Advanced search and filtering capabilities</li>
          <li>Paper collections and reading lists</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>

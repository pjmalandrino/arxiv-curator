<template>
  <span 
    :class="badgeClasses"
    class="px-2 py-1 text-xs font-semibold rounded-full"
  >
    {{ scorePercent }}%
  </span>
</template>

<script>
export default {
  name: 'ScoreBadge',
  props: {
    score: {
      type: Number,
      required: true
    }
  },
  computed: {
    scorePercent() {
      return Math.round(this.score * 100)
    },
    badgeClasses() {
      if (this.score >= 0.8) {
        return 'bg-green-100 text-green-800'
      } else if (this.score >= 0.6) {
        return 'bg-yellow-100 text-yellow-800'
      } else {
        return 'bg-gray-100 text-gray-800'
      }
    }
  }
}
</script>

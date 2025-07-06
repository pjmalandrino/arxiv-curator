<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div 
          :class="`p-3 rounded-lg bg-${color}-100`"
        >
          <component 
            :is="iconComponent" 
            :class="`h-6 w-6 text-${color}-600`"
          />
        </div>
      </div>
      <div class="ml-5">
        <p class="text-sm font-medium text-gray-500">
          {{ title }}
        </p>
        <p class="text-2xl font-semibold text-gray-900">
          {{ formattedValue }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  DocumentTextIcon, 
  ClockIcon, 
  ChartBarIcon 
} from '@heroicons/vue/24/outline'

export default {
  name: 'StatsCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [Number, String],
      required: true
    },
    icon: {
      type: String,
      default: 'document-text'
    },
    color: {
      type: String,
      default: 'blue'
    }
  },
  computed: {
    iconComponent() {
      const icons = {
        'document-text': DocumentTextIcon,
        'clock': ClockIcon,
        'chart-bar': ChartBarIcon
      }
      return icons[this.icon] || DocumentTextIcon
    },
    formattedValue() {
      if (typeof this.value === 'number' && this.value > 1000) {
        return (this.value / 1000).toFixed(1) + 'k'
      }
      return this.value
    }
  }
}
</script>

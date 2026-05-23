<template>
  <ProjectLayout>
    <WorkflowStageGrid :stages="stages" />
  </ProjectLayout>
</template>

<script setup lang="ts">
import WorkflowStageGrid from '@/components/workspace/WorkflowStageGrid.vue'
import { PRICING_WORKFLOW_STAGES } from '@/constants/workspace'
import ProjectLayout from '@/layouts/ProjectLayout.vue'

const stages = PRICING_WORKFLOW_STAGES
</script>

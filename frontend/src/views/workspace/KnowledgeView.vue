<template>
  <ProjectLayout>
    <WorkflowStageGrid :stages="stages" />
  </ProjectLayout>
</template>

<script setup lang="ts">
import WorkflowStageGrid from '@/components/workspace/WorkflowStageGrid.vue'
import { KNOWLEDGE_WORKFLOW_STAGES } from '@/constants/workspace'
import ProjectLayout from '@/layouts/ProjectLayout.vue'

const stages = KNOWLEDGE_WORKFLOW_STAGES
</script>

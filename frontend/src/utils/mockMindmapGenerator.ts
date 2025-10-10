// Mock mindmap generator for testing
export const generateMockMindmap = () => ({
  id: '1',
  title: 'Thought Flow',
  description: 'A mind mapping tool for organized thinking',
  color: '#fbbf24',
  x: 600,
  y: 300,
  children: [
    {
      id: '2',
      title: 'Frontend',
      description: 'User interface components',
      color: '#3b82f6',
      x: 400,
      y: 200,
      children: [
        {
          id: '5',
          title: 'React',
          description: 'Component library',
          color: '#06b6d4',
          x: 200,
          y: 150,
        },
        {
          id: '6',
          title: 'Components',
          description: 'UI elements',
          color: '#8b5cf6',
          x: 200,
          y: 250,
        }
      ]
    },
    {
      id: '3',
      title: 'Backend',
      description: 'Server-side logic',
      color: '#ef4444',
      x: 800,
      y: 200,
      children: [
        {
          id: '7',
          title: 'API',
          description: 'Data endpoints',
          color: '#f59e0b',
          x: 1000,
          y: 150,
        }
      ]
    },
    {
      id: '4',
      title: 'Planning',
      description: 'Project planning and documentation',
      color: '#10b981',
      x: 600,
      y: 500,
      children: [
        {
          id: '8',
          title: 'Features',
          description: 'Planned functionality',
          color: '#84cc16',
          x: 400,
          y: 400,
        },
        {
          id: '9',
          title: 'Timeline',
          description: 'Project milestones',
          color: '#ec4899',
          x: 800,
          y: 400,
        }
      ]
    }
  ]
});

// Mock function to generate mindmap data from uploaded files
export function generateMindmapFromFile(file: File): Promise<any> {
  return new Promise((resolve) => {
    // Simulate processing time
    setTimeout(() => {
      const fileName = file.name.toLowerCase();
      let mindmapData;

      if (fileName.includes('business') || fileName.includes('strategy')) {
        mindmapData = generateBusinessMindmap();
      } else if (fileName.includes('tech') || fileName.includes('programming')) {
        mindmapData = generateTechMindmap();
      } else if (fileName.includes('education') || fileName.includes('learning')) {
        mindmapData = generateEducationMindmap();
      } else {
        mindmapData = generateDefaultMindmap(file.name);
      }

      resolve(mindmapData);
    }, 3000); // 3 second delay to show processing screen
  });
}

function generateBusinessMindmap() {
  return {
    id: 'root',
    title: 'Business Strategy',
    description: 'Core business strategy framework',
    color: '#ddd6fe',
    x: 400,
    y: 200,
    children: [
      {
        id: 'market',
        title: 'Market Analysis',
        description: 'Understanding target market and competition',
        color: '#bfdbfe',
        x: 200,
        y: 100,
        children: [
          {
            id: 'competitors',
            title: 'Competitors',
            description: 'Analysis of competitive landscape',
            color: '#fed7d7',
            x: 50,
            y: 50
          },
          {
            id: 'customers',
            title: 'Target Customers',
            description: 'Customer segmentation and personas',
            color: '#d1fae5',
            x: 50,
            y: 150
          }
        ]
      },
      {
        id: 'operations',
        title: 'Operations',
        description: 'Core business operations and processes',
        color: '#fde68a',
        x: 600,
        y: 120,
        children: [
          {
            id: 'supply',
            title: 'Supply Chain',
            description: 'Supply chain management strategy',
            color: '#fbb6ce',
            x: 750,
            y: 60
          },
          {
            id: 'hr',
            title: 'Human Resources',
            description: 'Talent acquisition and management',
            color: '#c7d2fe',
            x: 750,
            y: 180
          }
        ]
      },
      {
        id: 'finance',
        title: 'Financial Planning',
        description: 'Revenue models and financial projections',
        color: '#a7f3d0',
        x: 500,
        y: 350,
        children: [
          {
            id: 'revenue',
            title: 'Revenue Streams',
            description: 'Multiple revenue generation strategies',
            color: '#fdba74',
            x: 350,
            y: 450
          },
          {
            id: 'costs',
            title: 'Cost Structure',
            description: 'Fixed and variable cost analysis',
            color: '#f9a8d4',
            x: 650,
            y: 450
          }
        ]
      }
    ]
  };
}

function generateTechMindmap() {
  return {
    id: 'root',
    title: 'Software Architecture',
    description: 'Modern software development architecture',
    color: '#ddd6fe',
    x: 400,
    y: 200,
    children: [
      {
        id: 'frontend',
        title: 'Frontend',
        description: 'User interface and experience layer',
        color: '#bfdbfe',
        x: 200,
        y: 100,
        children: [
          {
            id: 'react',
            title: 'React',
            description: 'Component-based UI framework',
            color: '#dbeafe',
            x: 50,
            y: 50
          },
          {
            id: 'styling',
            title: 'Styling',
            description: 'CSS frameworks and design systems',
            color: '#fecaca',
            x: 50,
            y: 150
          }
        ]
      },
      {
        id: 'backend',
        title: 'Backend',
        description: 'Server-side logic and data processing',
        color: '#d1fae5',
        x: 600,
        y: 120,
        children: [
          {
            id: 'api',
            title: 'REST API',
            description: 'RESTful web services',
            color: '#ecfdf5',
            x: 750,
            y: 60
          },
          {
            id: 'auth',
            title: 'Authentication',
            description: 'User authentication and authorization',
            color: '#fef3c7',
            x: 750,
            y: 180
          }
        ]
      },
      {
        id: 'database',
        title: 'Database',
        description: 'Data storage and management',
        color: '#fde68a',
        x: 500,
        y: 350,
        children: [
          {
            id: 'sql',
            title: 'SQL Database',
            description: 'Relational database management',
            color: '#fed7d7',
            x: 350,
            y: 450
          },
          {
            id: 'nosql',
            title: 'NoSQL',
            description: 'Document and graph databases',
            color: '#e0e7ff',
            x: 650,
            y: 450
          }
        ]
      }
    ]
  };
}

function generateEducationMindmap() {
  return {
    id: 'root',
    title: 'Learning Strategy',
    description: 'Effective learning methodology',
    color: '#ddd6fe',
    x: 400,
    y: 200,
    children: [
      {
        id: 'theory',
        title: 'Theoretical Foundation',
        description: 'Core concepts and principles',
        color: '#bfdbfe',
        x: 200,
        y: 100,
        children: [
          {
            id: 'concepts',
            title: 'Key Concepts',
            description: 'Fundamental building blocks',
            color: '#dbeafe',
            x: 50,
            y: 50
          },
          {
            id: 'models',
            title: 'Mental Models',
            description: 'Frameworks for understanding',
            color: '#fecaca',
            x: 50,
            y: 150
          }
        ]
      },
      {
        id: 'practice',
        title: 'Practical Application',
        description: 'Hands-on learning and exercises',
        color: '#d1fae5',
        x: 600,
        y: 120,
        children: [
          {
            id: 'projects',
            title: 'Projects',
            description: 'Real-world implementation',
            color: '#ecfdf5',
            x: 750,
            y: 60
          },
          {
            id: 'exercises',
            title: 'Exercises',
            description: 'Skill development activities',
            color: '#fef3c7',
            x: 750,
            y: 180
          }
        ]
      },
      {
        id: 'assessment',
        title: 'Assessment',
        description: 'Progress tracking and evaluation',
        color: '#fde68a',
        x: 500,
        y: 350,
        children: [
          {
            id: 'tests',
            title: 'Tests',
            description: 'Knowledge verification',
            color: '#fed7d7',
            x: 350,
            y: 450
          },
          {
            id: 'reflection',
            title: 'Reflection',
            description: 'Self-assessment and growth',
            color: '#e0e7ff',
            x: 650,
            y: 450
          }
        ]
      }
    ]
  };
}

function generateDefaultMindmap(fileName: string) {
  return {
    id: 'root',
    title: fileName.replace(/\.[^/.]+$/, ''), // Remove file extension
    description: 'Document analysis and key insights',
    color: '#ddd6fe',
    x: 400,
    y: 200,
    children: [
      {
        id: 'main-topics',
        title: 'Main Topics',
        description: 'Primary themes identified in the document',
        color: '#bfdbfe',
        x: 200,
        y: 100,
        children: [
          {
            id: 'topic1',
            title: 'Key Point 1',
            description: 'First major insight or topic',
            color: '#dbeafe',
            x: 50,
            y: 50
          },
          {
            id: 'topic2',
            title: 'Key Point 2',
            description: 'Second major insight or topic',
            color: '#fecaca',
            x: 50,
            y: 150
          }
        ]
      },
      {
        id: 'details',
        title: 'Supporting Details',
        description: 'Additional context and information',
        color: '#d1fae5',
        x: 600,
        y: 120,
        children: [
          {
            id: 'detail1',
            title: 'Supporting Evidence',
            description: 'Data and facts that support main points',
            color: '#ecfdf5',
            x: 750,
            y: 60
          },
          {
            id: 'detail2',
            title: 'Examples',
            description: 'Concrete examples and case studies',
            color: '#fef3c7',
            x: 750,
            y: 180
          }
        ]
      },
      {
        id: 'conclusions',
        title: 'Conclusions',
        description: 'Key takeaways and next steps',
        color: '#fde68a',
        x: 500,
        y: 350,
        children: [
          {
            id: 'insights',
            title: 'Insights',
            description: 'Important discoveries and learnings',
            color: '#fed7d7',
            x: 350,
            y: 450
          },
          {
            id: 'actions',
            title: 'Action Items',
            description: 'Recommended next steps',
            color: '#e0e7ff',
            x: 650,
            y: 450
          }
        ]
      }
    ]
  };
}
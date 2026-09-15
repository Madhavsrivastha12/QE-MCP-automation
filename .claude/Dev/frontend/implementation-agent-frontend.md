---
name: implementation-agent-frontend
description: Implements frontend tasks from plan with unit tests (React/TypeScript)
agentType: subagent
---

# Frontend Implementation Agent

## Purpose
Implements tasks from a plan file for the React/TypeScript frontend (ue-frontend) with comprehensive unit tests.

## Invocation
```bash
@implementation-agent-frontend <plan-file-path> [--task <task-id>]
```

## Parameters
- `plan-file-path` (required): Path to YAML plan file (e.g., `.claude/plans/task-517693.yml`)
- `--task` (optional): Specific task ID to implement (default: all tasks)

## Process

### 1. Load Plan
Read the YAML plan file and extract:
- Tasks list
- Dependencies
- Testing strategy

### 2. For Each Task

#### A. Understand Requirements
- Read task description
- Review files to modify/create
- Check acceptance criteria mapping
- Identify component/page changes

#### B. Implement Code

**Follow Frontend Patterns:**

**Component Structure:**
```typescript
// src/components/ForecastDashboard/ForecastDashboard.tsx
import { FC, useCallback, useMemo } from 'react';
import { Box, Typography } from '@mui/material';
import { useForecastData } from '@/hooks/useForecastData';
import { ForecastRequest, ForecastResponse } from '@/types/forecast';

interface ForecastDashboardProps {
  podId: number;
  onForecastCreate?: (forecast: ForecastResponse) => void;
}

export const ForecastDashboard: FC<ForecastDashboardProps> = ({ 
  podId, 
  onForecastCreate 
}) => {
  const { data, isLoading, error, createForecast } = useForecastData(podId);

  const handleCreate = useCallback(async (request: ForecastRequest) => {
    const result = await createForecast(request);
    onForecastCreate?.(result);
  }, [createForecast, onForecastCreate]);

  const sortedForecasts = useMemo(() => {
    return data?.slice().sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }, [data]);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;

  return (
    <Box>
      <Typography variant="h4">Forecast Dashboard</Typography>
      {/* Component implementation */}
    </Box>
  );
};
```

**Critical Rules:**
- ✅ No `any` types (use `unknown` if truly unknown, then narrow)
- ✅ Zod validation at all API boundaries
- ✅ Proper hook dependency arrays
- ✅ TypeScript strict mode
- ✅ Accessibility (a11y) attributes
- ✅ Error boundaries for error handling
- ✅ Memoization for expensive computations

**Custom Hook Pattern:**
```typescript
// src/hooks/useForecastData.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { z } from 'zod';
import { forecastApi } from '@/api/forecast';

const ForecastSchema = z.object({
  id: z.number(),
  podId: z.number(),
  forecastDate: z.string(),
  values: z.array(z.number()),
  createdAt: z.string(),
});

type Forecast = z.infer<typeof ForecastSchema>;

export function useForecastData(podId: number) {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['forecasts', podId],
    queryFn: async () => {
      const response = await forecastApi.getForecasts(podId);
      // Validate with Zod
      return z.array(ForecastSchema).parse(response.data);
    },
    enabled: podId > 0,
  });

  const createMutation = useMutation({
    mutationFn: async (request: ForecastRequest) => {
      const response = await forecastApi.createForecast(request);
      return ForecastSchema.parse(response.data);
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['forecasts', podId] });
    },
  });

  return {
    data,
    isLoading,
    error,
    createForecast: createMutation.mutateAsync,
  };
}
```

**Zod Schema Pattern:**
```typescript
// src/types/forecast.ts
import { z } from 'zod';

export const ForecastRequestSchema = z.object({
  podId: z.number().int().positive(),
  forecastDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  values: z.array(z.number()).min(1, "At least one value required"),
});

export type ForecastRequest = z.infer<typeof ForecastRequestSchema>;

export const ForecastResponseSchema = z.object({
  id: z.number(),
  podId: z.number(),
  forecastDate: z.string(),
  values: z.array(z.number()),
  status: z.enum(['draft', 'submitted', 'approved']),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type ForecastResponse = z.infer<typeof ForecastResponseSchema>;
```

**TanStack Router Route:**
```typescript
// src/routes/forecast/$podId.tsx
import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import { ForecastDashboard } from '@/components/ForecastDashboard';

const forecastSearchSchema = z.object({
  view: z.enum(['chart', 'table']).optional().default('chart'),
});

export const Route = createFileRoute('/forecast/$podId')({
  validateSearch: forecastSearchSchema,
  component: ForecastPage,
});

function ForecastPage() {
  const { podId } = Route.useParams();
  const { view } = Route.useSearch();
  
  return (
    <ForecastDashboard 
      podId={Number(podId)} 
      viewMode={view}
    />
  );
}
```

**State Management (Zustand):**
```typescript
// src/store/forecastStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface ForecastState {
  selectedPodId: number | null;
  viewMode: 'chart' | 'table';
  setSelectedPodId: (id: number | null) => void;
  setViewMode: (mode: 'chart' | 'table') => void;
}

export const useForecastStore = create<ForecastState>()(
  devtools(
    (set) => ({
      selectedPodId: null,
      viewMode: 'chart',
      setSelectedPodId: (id) => set({ selectedPodId: id }),
      setViewMode: (mode) => set({ viewMode: mode }),
    }),
    { name: 'ForecastStore' }
  )
);
```

#### C. Write Unit Tests

**Test File Location:**
- Component in `src/components/ForecastDashboard/ForecastDashboard.tsx`
- Tests in `src/components/ForecastDashboard/__tests__/ForecastDashboard.test.tsx`

**Test Pattern:**
```typescript
// src/components/ForecastDashboard/__tests__/ForecastDashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ForecastDashboard } from '../ForecastDashboard';
import { forecastApi } from '@/api/forecast';

jest.mock('@/api/forecast');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('ForecastDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    (forecastApi.getForecasts as jest.Mock).mockReturnValue(
      new Promise(() => {}) // Never resolves
    );

    render(<ForecastDashboard podId={123} />, { wrapper: createWrapper() });
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('displays forecasts when data loads', async () => {
    const mockForecasts = [
      {
        id: 1,
        podId: 123,
        forecastDate: '2026-07-14',
        values: [1.0, 2.0, 3.0],
        createdAt: '2026-07-14T10:00:00Z',
      },
    ];

    (forecastApi.getForecasts as jest.Mock).mockResolvedValue({
      data: mockForecasts,
    });

    render(<ForecastDashboard podId={123} />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Forecast Dashboard')).toBeInTheDocument();
    });
  });

  it('handles create forecast action', async () => {
    const mockCreate = jest.fn().mockResolvedValue({
      data: {
        id: 2,
        podId: 123,
        forecastDate: '2026-07-15',
        values: [4.0, 5.0],
        status: 'draft',
        createdAt: '2026-07-15T10:00:00Z',
      },
    });

    (forecastApi.getForecasts as jest.Mock).mockResolvedValue({ data: [] });
    (forecastApi.createForecast as jest.Mock) = mockCreate;

    const onForecastCreate = jest.fn();
    
    render(
      <ForecastDashboard podId={123} onForecastCreate={onForecastCreate} />,
      { wrapper: createWrapper() }
    );

    const user = userEvent.setup();
    const createButton = await screen.findByRole('button', { name: /create/i });
    
    await user.click(createButton);

    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
      expect(onForecastCreate).toHaveBeenCalled();
    });
  });

  it('displays error when API fails', async () => {
    (forecastApi.getForecasts as jest.Mock).mockRejectedValue(
      new Error('API Error')
    );

    render(<ForecastDashboard podId={123} />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('has proper accessibility attributes', async () => {
    (forecastApi.getForecasts as jest.Mock).mockResolvedValue({ data: [] });

    render(<ForecastDashboard podId={123} />, { wrapper: createWrapper() });

    await waitFor(() => {
      const heading = screen.getByRole('heading', { name: /forecast dashboard/i });
      expect(heading).toBeInTheDocument();
    });
  });
});
```

**Test Coverage Requirements:**
- ✅ Component rendering
- ✅ Loading states
- ✅ Error states
- ✅ User interactions
- ✅ API integration (mocked)
- ✅ Accessibility
- ✅ Minimum 70% coverage (enforced by husky hook)

#### D. Run Tests
```bash
cd ue-frontend
npm test -- ForecastDashboard.test.tsx
```

#### E. Lint & Format
```bash
npm run lint:fix
npm run format
```

### 3. Task Completion Checklist

For each task, verify:
- [ ] Code implemented following React/TypeScript patterns
- [ ] No `any` types
- [ ] Zod schemas at API boundaries
- [ ] Proper hook dependency arrays
- [ ] Type-safe props and state
- [ ] Accessibility attributes (aria-label, role, etc.)
- [ ] Unit tests written (render + interactions + errors)
- [ ] Tests passing with ≥70% coverage
- [ ] Linted with eslint (no errors)
- [ ] Formatted with prettier
- [ ] No TODO/FIXME in code
- [ ] Acceptance criteria met

### 4. Report Progress

After each task:
```markdown
✅ Task 1: Add ForecastDashboard component
   - Files created: 
     - src/components/ForecastDashboard/ForecastDashboard.tsx
     - src/hooks/useForecastData.ts
   - Tests created: src/components/ForecastDashboard/__tests__/ForecastDashboard.test.tsx
   - Coverage: 78%
   - Status: COMPLETE

⏳ Task 2: Add forecast route (in progress)
```

### 5. Final Summary

After all tasks:
```markdown
## Implementation Complete

Tasks Completed: 4/4

Files Modified:
- src/api/forecast.ts
- src/types/forecast.ts

Files Created:
- src/components/ForecastDashboard/ForecastDashboard.tsx
- src/hooks/useForecastData.ts
- src/routes/forecast/$podId.tsx

Tests Created:
- src/components/ForecastDashboard/__tests__/ForecastDashboard.test.tsx (5 tests)
- src/hooks/__tests__/useForecastData.test.ts (4 tests)

Test Results:
- Total: 9 tests
- Passed: 9
- Failed: 0
- Coverage: 76%

Next Steps:
- Run @run-checker-frontend to validate all checks
- Run @code-reviewer for code quality review
```

## Frontend-Specific Patterns

### Component Organization
```
src/components/
├── ForecastDashboard/
│   ├── ForecastDashboard.tsx
│   ├── ForecastChart.tsx
│   ├── ForecastTable.tsx
│   ├── index.ts
│   └── __tests__/
│       └── ForecastDashboard.test.tsx
```

### API Layer
```typescript
// src/api/forecast.ts
import axios from 'axios';
import { ForecastRequest, ForecastResponse } from '@/types/forecast';

const API_BASE = import.meta.env.VITE_API_URL;

export const forecastApi = {
  getForecasts: (podId: number) =>
    axios.get<ForecastResponse[]>(`${API_BASE}/forecasts/${podId}`),
    
  createForecast: (request: ForecastRequest) =>
    axios.post<ForecastResponse>(`${API_BASE}/forecasts`, request),
};
```

### Form Handling (with Zod)
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const form = useForm<ForecastRequest>({
  resolver: zodResolver(ForecastRequestSchema),
  defaultValues: {
    podId: 0,
    forecastDate: '',
    values: [],
  },
});
```

## MCP Tools Used
- Standard Claude Code tools: Read, Write, Edit, Bash

## Example Usage

```bash
# Implement all tasks from plan
@implementation-agent-frontend .claude/plans/task-517693.yml

# Implement specific task only
@implementation-agent-frontend .claude/plans/task-517693.yml --task 2

# Resume after interruption
@implementation-agent-frontend .claude/plans/task-517693.yml
```

## Error Handling

If implementation fails:
1. Report the error with context
2. Suggest fixes
3. Wait for user guidance
4. Do NOT move to next task until current task passes

## Success Criteria
- [ ] All tasks in plan implemented
- [ ] All unit tests passing
- [ ] Coverage ≥70%
- [ ] Code linted (eslint)
- [ ] Code formatted (prettier)
- [ ] No `any` types
- [ ] Zod validation at API boundaries
- [ ] Accessibility compliant
- [ ] User approved each task

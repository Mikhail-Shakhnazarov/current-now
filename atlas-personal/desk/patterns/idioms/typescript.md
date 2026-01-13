# TypeScript Idioms

Style patterns for TypeScript execution.

---

## Strict Mode

Always enable in tsconfig:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true
  }
}
```

## Interfaces vs Types

Interfaces for objects:
```typescript
interface Signal {
  intent: string;
  type: 'task' | 'decision' | 'question';
  references: string[];
}
```

Types for unions and computed types:
```typescript
type SpecStatus = 'draft' | 'active' | 'complete' | 'superseded';
type RequirementLevel = keyof Spec['requirements'];
```

## Null Safety

Explicit narrowing:
```typescript
function process(value: string | null): string {
  if (value === null) {
    return 'default';
  }
  return value.toUpperCase();
}
```

## Generics

Constrained generics for flexibility with safety:
```typescript
function loadSchema<T extends object>(path: string): T {
  const content = readFileSync(path, 'utf-8');
  return JSON.parse(content) as T;
}
```

## Runtime Validation

Use Zod for runtime schema validation:
```typescript
import { z } from 'zod';

const SignalSchema = z.object({
  intent: z.string(),
  type: z.enum(['task', 'decision', 'question']),
  references: z.array(z.string()),
});

type Signal = z.infer<typeof SignalSchema>;
```

# JavaScript Idioms

Style patterns for JavaScript execution.

---

## Modules

ES modules for all new code:
```javascript
import { readFile } from 'fs/promises';
export function processSignal(signal) { ... }
```

## Async/Await

Prefer async/await over promise chains:
```javascript
async function loadSpec(path) {
  try {
    const data = await readFile(path, 'utf-8');
    return JSON.parse(data);
  } catch (err) {
    throw new Error(`Failed to load spec: ${err.message}`);
  }
}
```

## Immutability

Spread for state updates:
```javascript
const newState = { ...state, count: state.count + 1 };
const newArray = [...items, newItem];
```

## Null Handling

Explicit checks:
```javascript
if (value != null) {
  process(value);
}
```

## React Patterns

Hooks at top level:
```javascript
function Component({ data }) {
  const [state, setState] = useState(initialState);
  const handleClick = useCallback(() => { ... }, [dependency]);
  
  useEffect(() => {
    let cancelled = false;
    async function fetch() {
      const result = await loadData();
      if (!cancelled) setState(result);
    }
    fetch();
    return () => { cancelled = true; };
  }, []);
  
  return <div>...</div>;
}
```

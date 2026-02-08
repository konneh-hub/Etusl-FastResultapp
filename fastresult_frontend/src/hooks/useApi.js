import { useState, useEffect, useCallback, useRef } from 'react';

// useApi accepts an async function (fn) which performs the API call and returns data.
// It follows the required pattern: { data, loading, error, refresh }
export default function useApi(fn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const mounted = useRef(true);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fn(...args);
      if (mounted.current) setData(result);
      return result;
    } catch (err) {
      if (mounted.current) setError(err);
      throw err;
    } finally {
      if (mounted.current) setLoading(false);
    }
  }, // eslint-disable-next-line
  deps);

  useEffect(() => {
    mounted.current = true;
    // Fetch once on mount
    execute();
    return () => { mounted.current = false; };
  }, [execute]);

  const refresh = useCallback(() => execute(), [execute]);

  return { data, loading, error, refresh };
}

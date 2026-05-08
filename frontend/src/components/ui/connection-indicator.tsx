import { useEffect, useState } from 'react';

import { getHealth } from '../../lib/api';

type ConnectionState = 'checking' | 'online' | 'offline';

const stateClasses: Record<ConnectionState, string> = {
  checking: 'border-white/10 bg-white/5 text-mist/70',
  online: 'border-moss/35 bg-moss/15 text-moss',
  offline: 'border-ember/35 bg-ember/15 text-ember',
};

const dotClasses: Record<ConnectionState, string> = {
  checking: 'bg-mist/70',
  online: 'bg-moss',
  offline: 'bg-ember',
};

const labels: Record<ConnectionState, string> = {
  checking: 'Comprobando backend',
  online: 'Backend conectado',
  offline: 'Backend no disponible',
};

export function ConnectionIndicator() {
  const [connectionState, setConnectionState] = useState<ConnectionState>('checking');

  useEffect(() => {
    let active = true;

    const checkConnection = async () => {
      try {
        const response = await getHealth();

        if (active) {
          setConnectionState(response.ok ? 'online' : 'offline');
        }
      }
      catch {
        if (active) {
          setConnectionState('offline');
        }
      }
    };

    void checkConnection();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className={`inline-flex items-center gap-3 rounded-full border px-4 py-2 text-sm ${stateClasses[connectionState]}`}>
      <span className={`h-2.5 w-2.5 rounded-full ${dotClasses[connectionState]}`} />
      <span>{labels[connectionState]}</span>
    </div>
  );
}
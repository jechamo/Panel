import { FlowCanvas } from './components/canvas/flow-canvas';
import { NodeConfigPanel } from './components/panels/node-config-panel';
import { ConnectionIndicator } from './components/ui/connection-indicator';
import { FlowPersistenceBar } from './components/ui/flow-persistence-bar';

export default function App() {
	return (
		<div className="min-h-screen bg-ink bg-haze text-mist">
			<div className="mx-auto flex min-h-screen max-w-[1600px] flex-col px-4 py-4 sm:px-6 lg:px-8">
				<header className="mb-4 flex flex-col gap-4 rounded-[32px] border border-white/10 bg-panel/70 px-6 py-5 shadow-glow backdrop-blur md:flex-row md:items-end md:justify-between">
					<div className="max-w-3xl">
						<p className="text-xs uppercase tracking-[0.35em] text-tide/80">Panel</p>
						<h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
							Canvas local para encadenar agentes y microservicios
						</h1>
						<p className="mt-3 text-sm text-mist/72 sm:text-base">
							Fase 2 deja listo el lienzo visual con nodos dummy, zoom, pan y conexiones.
						</p>
					</div>

					<div className="flex flex-col gap-3 md:items-end">
						<ConnectionIndicator />
						<FlowPersistenceBar />
						<div className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-mist/72">
							Los flujos ahora se guardan como JSON versionado en backend/storage/flows/.
						</div>
					</div>
				</header>

				<div className="flex flex-1 flex-col gap-4 lg:flex-row">
					<main className="flex-1 overflow-hidden rounded-[36px] border border-white/10 bg-panel/80 shadow-glow backdrop-blur">
						<FlowCanvas />
					</main>

					<NodeConfigPanel />
				</div>
			</div>
		</div>
	);
}
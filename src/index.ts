import { Container, getContainer } from "@cloudflare/containers";

export class EvalViewerContainer extends Container {
  defaultPort = 8080;
  sleepAfter = "10m";
}

interface Env {
  EVAL_VIEWER: DurableObjectNamespace<EvalViewerContainer>;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/healthz") {
      return new Response("ok", {
        headers: {
          "content-type": "text/plain; charset=utf-8"
        }
      });
    }

    return getContainer(env.EVAL_VIEWER, "world-cup-picks-report").fetch(request);
  }
} satisfies ExportedHandler<Env>;

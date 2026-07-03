import { Container, getContainer } from "@cloudflare/containers";

export class EvalViewerContainer extends Container {
  defaultPort = 8080;
  sleepAfter = "10m";
}

interface Env {
  EVAL_VIEWER: DurableObjectNamespace<EvalViewerContainer>;
  GA_MEASUREMENT_ID?: string;
}

function googleAnalyticsSnippet(measurementId: string): string {
  const id = JSON.stringify(measurementId);
  const encodedId = encodeURIComponent(measurementId);

  return `
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=${encodedId}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', ${id});

      (() => {
        const sendPageView = () => {
          if (typeof window.gtag === "function") {
            window.gtag("event", "page_view", {
              page_location: window.location.href,
              page_path: window.location.pathname + window.location.search + window.location.hash,
              page_title: document.title,
              send_to: ${id}
            });
          }
        };

        const wrap = (type) => {
          const original = history[type];
          history[type] = function (...args) {
            const result = original.apply(this, args);
            queueMicrotask(sendPageView);
            return result;
          };
        };

        wrap("pushState");
        wrap("replaceState");
        window.addEventListener("popstate", sendPageView);
      })();
    </script>
  `;
}

async function injectGoogleAnalytics(
  response: Response,
  measurementId?: string
): Promise<Response> {
  if (!measurementId) {
    return response;
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("text/html")) {
    return response;
  }

  const html = await response.text();
  if (!html.includes("</head>") || html.includes("googletagmanager.com/gtag/js")) {
    return new Response(html, response);
  }

  const headers = new Headers(response.headers);
  headers.delete("content-encoding");
  headers.delete("content-length");

  return new Response(
    html.replace("</head>", `${googleAnalyticsSnippet(measurementId)}</head>`),
    {
      status: response.status,
      statusText: response.statusText,
      headers
    }
  );
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

    const response = await getContainer(env.EVAL_VIEWER, "world-cup-picks-report").fetch(
      request
    );

    return injectGoogleAnalytics(response, env.GA_MEASUREMENT_ID);
  }
} satisfies ExportedHandler<Env>;

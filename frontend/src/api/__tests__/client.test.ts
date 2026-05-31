import { afterEach, describe, expect, it, vi } from "vitest";

import { analyzeImage, fetchReferences } from "../client";

const file = new File(["bytes"], "face.png", { type: "image/png" });

afterEach(() => {
  vi.restoreAllMocks();
});

describe("analyzeImage", () => {
  it("posts the file as multipart and returns the parsed body", async () => {
    const body = { face_detected: true };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(body),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await analyzeImage(file);

    expect(fetchMock).toHaveBeenCalledWith("/analyze", expect.objectContaining({ method: "POST" }));
    const sentBody = fetchMock.mock.calls[0][1].body as FormData;
    expect(sentBody.get("file")).toBe(file);
    expect(result).toEqual(body);
  });

  it("throws with the API detail message on a non-ok response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: "Unsupported upload type." }),
      }),
    );

    await expect(analyzeImage(file)).rejects.toThrow("Unsupported upload type.");
  });
});

describe("fetchReferences", () => {
  it("loads the reference bands from /references", async () => {
    const payload = { references: [], disclaimer: "context only", sources: [] };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(payload) });
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchReferences();

    expect(fetchMock).toHaveBeenCalledWith("/references");
    expect(result).toEqual(payload);
  });
});

class MuapiClient {
  async generateImage(params) {
    return this.fakeResponse("image");
  }

   async generateVideo(params) {
    const res = await fetch("http://localhost:8001/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: params.prompt || "hello world",
      }),
    });

    return await res.json();
  }

  async generateI2I(params) {
    return this.fakeResponse("image");
  }

  async generateI2V(params) {
    return this.fakeResponse("video");
  }

  async processV2V(params) {
    return this.fakeResponse("video");
  }

  async processLipSync(params) {
    return this.fakeResponse("video");
  }

  async uploadFile(file) {
    return "https://samplelib.com/lib/preview/mp4/sample-5s.mp4";
  }

  async pollForResult() {
    return this.fakeResponse("video");
  }

  async fakeResponse(type) {
    return {
      requestId: "local-test",
      url:
        type === "image"
          ? "https://picsum.photos/512/512"
          : "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
    };
  }
}

export const muapi = new MuapiClient();

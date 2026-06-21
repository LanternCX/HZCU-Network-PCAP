import os

from litellm import completion


def context_preview(repository, capture_id):
    capture = repository.get_capture(capture_id)
    stats = repository.stats(capture_id)
    packets = repository.list_packets(capture_id, {"page": 1, "page_size": 5})["items"]
    return {
        "capture": {
            "id": capture["id"],
            "filename": capture["original_name"],
            "packet_count": capture["packet_count"],
            "duration_seconds": capture["duration_seconds"],
            "status": capture["status"],
        },
        "protocols": stats["protocols"],
        "traffic_trend": stats["traffic_trend"][:20],
        "top_sources": stats["top_sources"],
        "top_destinations": stats["top_destinations"],
        "top_ports": stats["top_ports"],
        "packet_sample": [
            {
                "number": p["number"],
                "timestamp": p["timestamp"],
                "src_ip": p["src_ip"],
                "dst_ip": p["dst_ip"],
                "protocol": p["protocol"],
                "length": p["length"],
            }
            for p in packets
        ],
        "saved_summary": repository.get_ai_summary(capture_id),
    }


def stream_summary(repository, capture_id):
    settings = repository.settings()
    api_key = settings.get("api_key") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("LITELLM_API_KEY")
    if not api_key:
        yield "AI is not configured. Add API settings before starting analysis."
        return
    context = context_preview(repository, capture_id)
    streaming = settings["streaming"] == "true"
    try:
        response = completion(
            model=settings["model"],
            custom_llm_provider="deepseek" if "deepseek" in settings["api_base"] and "/" not in settings["model"] else None,
            api_base=settings["api_base"],
            api_key=api_key,
            stream=streaming,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Summarize this analyzed packet capture. Focus on anomalies, "
                        f"traffic spikes, endpoints, protocols, and risks:\n{context}"
                    ),
                }
            ],
        )
    except Exception as exc:
        yield f"AI analysis failed. {exc}"
        return
    if not streaming:
        text = response["choices"][0]["message"].get("content", "")
        repository.save_ai_summary(capture_id, text)
        yield text
        return
    chunks = []
    for chunk in response:
        text = chunk["choices"][0]["delta"].get("content", "")
        if text:
            chunks.append(text)
            yield text
    if chunks:
        repository.save_ai_summary(capture_id, "".join(chunks))

def validate_pdf_bytes(pdf_bytes: bytes) -> None:
    if not pdf_bytes:
        raise ValueError("Empty PDF content.")


# Gemini 멀티모달 입력으로 허용하는 문서 MIME 타입
SUPPORTED_DOCUMENT_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
}


def _sniff_mime_type(file_bytes: bytes) -> str | None:
    """매직 바이트로 MIME 타입을 추론한다. (S3 ContentType이 없거나 신뢰할 수 없을 때 폴백)"""
    if file_bytes.startswith(b"%PDF"):
        return "application/pdf"
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return "image/webp"
    return None


def resolve_document_mime_type(content_type: str | None, file_bytes: bytes) -> str:
    """
    S3 ContentType을 우선 사용하되, 없거나 지원하지 않는 값이면 매직 바이트로 추론한다.
    최종적으로 지원하지 않는 형식이면 ValueError를 던진다.
    """
    if not file_bytes:
        raise ValueError("Empty document content.")

    normalized = (content_type or "").split(";")[0].strip().lower()
    if normalized in SUPPORTED_DOCUMENT_MIME_TYPES:
        return normalized

    sniffed = _sniff_mime_type(file_bytes)
    if sniffed in SUPPORTED_DOCUMENT_MIME_TYPES:
        return sniffed

    raise ValueError(
        f"지원하지 않는 문서 형식입니다. content_type={content_type!r}, sniffed={sniffed!r}. "
        f"지원 형식: {sorted(SUPPORTED_DOCUMENT_MIME_TYPES)}"
    )

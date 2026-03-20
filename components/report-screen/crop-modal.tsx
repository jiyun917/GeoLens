"use client";

import { useRef, useState, useCallback, useEffect } from "react";

interface CropModalProps {
  imageSrc: string;
  onConfirm: (croppedImage: string) => void;
  onCancel: () => void;
}

interface Selection {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
}

export function CropModal({ imageSrc, onConfirm, onCancel }: CropModalProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const layoutRef = useRef({ scale: 1, offsetX: 0, offsetY: 0 });

  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      imageRef.current = img;
      setImageLoaded(true);
    };
    img.src = imageSrc;
  }, [imageSrc]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    if (!canvas || !img || !imageLoaded) return;

    const dpr = window.devicePixelRatio || 1;
    const cw = window.innerWidth;
    const ch = window.innerHeight;

    // Set canvas pixel size accounting for device pixel ratio
    canvas.width = cw * dpr;
    canvas.height = ch * dpr;
    canvas.style.width = cw + "px";
    canvas.style.height = ch + "px";

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    // Fit image to screen (letterbox)
    const scale = Math.min(cw / img.width, ch / img.height);
    const drawW = img.width * scale;
    const drawH = img.height * scale;
    const offsetX = (cw - drawW) / 2;
    const offsetY = (ch - drawH) / 2;

    layoutRef.current = { scale, offsetX, offsetY };

    // Black background
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, cw, ch);

    // Draw image
    ctx.drawImage(img, offsetX, offsetY, drawW, drawH);

    // Dim overlay
    ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
    ctx.fillRect(0, 0, cw, ch);

    if (selection) {
      const x = Math.min(selection.startX, selection.endX);
      const y = Math.min(selection.startY, selection.endY);
      const w = Math.abs(selection.endX - selection.startX);
      const h = Math.abs(selection.endY - selection.startY);

      if (w > 2 && h > 2) {
        // Redraw bright image only in selected area using clipping
        ctx.save();
        ctx.beginPath();
        ctx.rect(x, y, w, h);
        ctx.clip();
        ctx.fillStyle = "#000";
        ctx.fillRect(x, y, w, h);
        ctx.drawImage(img, offsetX, offsetY, drawW, drawH);
        ctx.restore();

        // Selection border
        ctx.strokeStyle = "#3b82f6";
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);
      }
    }

    // Instructions
    if (!isDragging) {
      const text = "Drag to select region. Press ESC to cancel.";
      ctx.font = "14px sans-serif";
      const tw = ctx.measureText(text).width + 24;
      ctx.fillStyle = "rgba(0,0,0,0.7)";
      ctx.fillRect(cw / 2 - tw / 2, 10, tw, 30);
      ctx.fillStyle = "#fff";
      ctx.textAlign = "center";
      ctx.fillText(text, cw / 2, 30);
      ctx.textAlign = "start";
    }
  }, [selection, imageLoaded, isDragging]);

  useEffect(() => {
    draw();
  }, [draw]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setSelection({
      startX: e.clientX,
      startY: e.clientY,
      endX: e.clientX,
      endY: e.clientY,
    });
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isDragging) return;
      setSelection((prev) =>
        prev ? { ...prev, endX: e.clientX, endY: e.clientY } : null
      );
    },
    [isDragging]
  );

  const handleMouseUp = useCallback(() => {
    if (!isDragging || !selection) return;
    setIsDragging(false);

    const w = Math.abs(selection.endX - selection.startX);
    const h = Math.abs(selection.endY - selection.startY);

    if (w > 10 && h > 10) {
      cropAndConfirm(selection);
    }
  }, [isDragging, selection]);

  const cropAndConfirm = (sel: Selection) => {
    const img = imageRef.current;
    if (!img) return;

    const { scale, offsetX, offsetY } = layoutRef.current;

    const x = Math.min(sel.startX, sel.endX);
    const y = Math.min(sel.startY, sel.endY);
    const w = Math.abs(sel.endX - sel.startX);
    const h = Math.abs(sel.endY - sel.startY);

    // Convert screen coordinates to original image coordinates
    const imgX = Math.max(0, (x - offsetX) / scale);
    const imgY = Math.max(0, (y - offsetY) / scale);
    const imgW = Math.min(w / scale, img.width - imgX);
    const imgH = Math.min(h / scale, img.height - imgY);

    if (imgW < 5 || imgH < 5) {
      onConfirm(imageSrc);
      return;
    }

    const cropCanvas = document.createElement("canvas");
    cropCanvas.width = Math.round(imgW);
    cropCanvas.height = Math.round(imgH);
    const ctx = cropCanvas.getContext("2d");
    if (!ctx) {
      onConfirm(imageSrc);
      return;
    }

    ctx.drawImage(
      img,
      Math.round(imgX),
      Math.round(imgY),
      Math.round(imgW),
      Math.round(imgH),
      0,
      0,
      Math.round(imgW),
      Math.round(imgH)
    );

    onConfirm(cropCanvas.toDataURL("image/jpeg", 0.9));
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onCancel]);

  return (
    <div className="fixed inset-0 z-[100]">
      <canvas
        ref={canvasRef}
        className="cursor-crosshair"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      />
    </div>
  );
}

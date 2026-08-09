import { type RefObject, useEffect, useState } from "react";

const clamp = (value: number) => Math.min(1, Math.max(0, value));

function sceneProgress(element: HTMLElement | null) {
  if (!element) return 0;
  const viewport = window.innerHeight;
  const rect = element.getBoundingClientRect();
  const travel = Math.max(1, rect.height - viewport);
  return clamp(-rect.top / travel);
}

export function useLandingCinematics(
  rootRef: RefObject<HTMLElement | null>,
  heroRef: RefObject<HTMLElement | null>,
  loopRef: RefObject<HTMLElement | null>,
  stepCount: number,
) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const compactLayout = window.matchMedia("(max-width: 900px)");
    const revealNodes = Array.from(root.querySelectorAll<HTMLElement>("[data-reveal]"));
    const heroLines = Array.from(root.querySelectorAll<HTMLElement>("[data-hero-line]"));
    const heroProduct = root.querySelector<HTMLElement>("[data-hero-product]");
    const heroMeta = Array.from(root.querySelectorAll<HTMLElement>("[data-hero-meta]"));
    const heroCue = root.querySelector<HTMLElement>("[data-hero-cue]");
    const parallaxNodes = Array.from(root.querySelectorAll<HTMLElement>("[data-parallax]"));

    const revealEverything = () => {
      revealNodes.forEach((node) => node.classList.add("is-visible"));
      heroLines.forEach((line) => {
        line.style.opacity = "1";
        line.style.transform = "none";
        line.style.filter = "none";
      });
      if (heroProduct) {
        heroProduct.style.opacity = "1";
        heroProduct.style.transform = "none";
        heroProduct.style.filter = "none";
      }
      heroMeta.forEach((node) => { node.style.opacity = "1"; });
      if (heroCue) heroCue.style.opacity = "1";
    };

    if (reducedMotion.matches || compactLayout.matches) {
      revealEverything();
      return;
    }

    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add("is-visible");
        });
      },
      { rootMargin: "0px 0px -9% 0px", threshold: 0.12 },
    );
    revealNodes.forEach((node) => revealObserver.observe(node));

    let raf = 0;
    let lastActiveStep = -1;

    const update = () => {
      raf = 0;
      const hero = sceneProgress(heroRef.current);
      const loop = sceneProgress(loopRef.current);

      root.style.setProperty("--hero-progress", hero.toFixed(4));
      root.style.setProperty("--loop-progress", loop.toFixed(4));

      heroLines.forEach((line, index) => {
        const local = clamp(hero * 1.82 - index * 0.18);
        const lift = 68 * (1 - local);
        const tilt = -14 * (1 - local);
        const blur = 12 * (1 - local);
        line.style.opacity = String(local);
        line.style.transform = `translate3d(0, ${lift}px, 0) rotateX(${tilt}deg)`;
        line.style.filter = `blur(${blur}px)`;
      });

      const metaProgress = clamp(hero * 2.4);
      heroMeta.forEach((node) => { node.style.opacity = String(metaProgress); });

      const productProgress = clamp(hero * 1.65 - 0.28);
      if (heroProduct) {
        heroProduct.style.opacity = String(productProgress);
        heroProduct.style.transform = `translate3d(0, ${86 * (1 - productProgress)}px, 0) scale(${0.92 + productProgress * 0.08}) rotateX(${5 * (1 - productProgress)}deg)`;
        heroProduct.style.filter = `blur(${10 * (1 - productProgress)}px)`;
      }

      if (heroCue) heroCue.style.opacity = String(clamp(1 - hero * 3.5));

      parallaxNodes.forEach((node) => {
        const speed = Number(node.dataset.parallax ?? "0.08");
        const rect = node.getBoundingClientRect();
        const centerOffset = (rect.top + rect.height / 2 - window.innerHeight / 2) / window.innerHeight;
        node.style.setProperty("--parallax-y", `${centerOffset * speed * -120}px`);
      });

      const nextStep = Math.min(stepCount - 1, Math.floor(clamp(loop * 0.9999) * stepCount));
      if (nextStep !== lastActiveStep) {
        lastActiveStep = nextStep;
        setActiveStep(nextStep);
      }
    };

    const schedule = () => {
      if (!raf) raf = window.requestAnimationFrame(update);
    };

    const onPointerMove = (event: PointerEvent) => {
      root.style.setProperty("--pointer-x", `${event.clientX}px`);
      root.style.setProperty("--pointer-y", `${event.clientY}px`);
    };

    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    root.addEventListener("pointermove", onPointerMove, { passive: true });
    update();

    return () => {
      revealObserver.disconnect();
      if (raf) window.cancelAnimationFrame(raf);
      window.removeEventListener("scroll", schedule);
      window.removeEventListener("resize", schedule);
      root.removeEventListener("pointermove", onPointerMove);
    };
  }, [heroRef, loopRef, rootRef, stepCount]);

  return activeStep;
}

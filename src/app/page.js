"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import SplitType from "split-type";
import { items } from "@/data/items";
import styles from "./page.module.css";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const itemPositionsLarge = [
  { top: "5%", left: "7%" },
  { top: "23%", left: "27%" },
  { top: "75%", left: "75%" },
  { top: "25%", left: "75%" },
  { top: "10%", left: "50%" },
  { top: "70%", left: "55%" },
  { top: "50%", left: "5%" },
  { top: "65%", left: "25%" },
];

const itemPositionsSmall = [
  { top: "2%", left: "7%" },
  { top: "30%", left: "27%" },
  { top: "40%", left: "75%" },
  { top: "5%", left: "75%" },
  { top: "10%", left: "43%" },
  { top: "70%", left: "75%" },
  { top: "50%", left: "5%" },
  { top: "65%", left: "35%" },
];

export default function Home() {
  const galleryRef = useRef(null);
  const aboutRef = useRef(null);

  // About text reveal animation
  useEffect(() => {
    const el = aboutRef.current;
    if (!el) return;

    gsap.registerPlugin(ScrollTrigger);

    const bg = el.dataset.bgColor;
    const fg = el.dataset.fgColor;

    const text = new SplitType(el, { types: "words" });

    const ctx = gsap.context(() => {
      gsap.fromTo(
        text.words,
        { color: bg },
        {
          color: fg,
          duration: 0.3,
          stagger: 0.02,
          scrollTrigger: {
            trigger: el,
            start: "top 80%",
            end: "top 20%",
            scrub: true,
            toggleActions: "play play reverse reverse",
          },
        }
      );
    });

    return () => {
      ctx.revert();
      text.revert();
    };
  }, []);

  // Gallery parallax
  useEffect(() => {
    const gallery = galleryRef.current;
    if (!gallery) return;

    function updateGalleryPositions() {
      gallery.innerHTML = "";

      const itemPositions =
        window.innerWidth < 768 ? itemPositionsSmall : itemPositionsLarge;

      items.forEach((itemData, index) => {
        if (itemData.id >= 0 && itemData.id <= 10) {
          const item = document.createElement("div");
          item.classList.add(styles.item);

          const position = itemPositions[index];
          item.style.top = position.top;
          item.style.left = position.left;

          const img = document.createElement("img");
          img.src = itemData.img;
          img.classList.add(styles.itemImg);
          item.appendChild(img);

          gallery.appendChild(item);
        }
      });
    }

    updateGalleryPositions();
    window.addEventListener("resize", updateGalleryPositions);

    function handleMouseMove(e) {
      gallery.querySelectorAll(`.${styles.item}`).forEach((item, index) => {
        const animationFactor = items[index].parllaxSpeed;
        const deltaX = (e.clientX - window.innerWidth / 2) * animationFactor;
        const deltaY = (e.clientY - window.innerHeight / 2) * animationFactor;
        gsap.to(item, { x: deltaX, y: deltaY, duration: 0.75 });
      });
    }

    document.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("resize", updateGalleryPositions);
      document.removeEventListener("mousemove", handleMouseMove);
      gsap.killTweensOf(gallery.querySelectorAll(`.${styles.item}`));
    };
  }, []);

  return (
    <main>
      {/* Hero Mobile */}
      <section className={styles.section}>
        <div className={styles.containerHm}>
          <h1 className={styles.logoHm}>Mutti</h1>
          <img
            src="https://www.furche.at/images/content/5676700-1920x1080c-Raute.jpg"
            alt=""
            className={styles.imgHm}
          />
        </div>
      </section>

      {/* About */}
      <section
        className={styles.about}
        ref={aboutRef}
        data-bg-color="#1d1d1d"
        data-fg-color="white"
      >
        <p>
          Mutti is a project featuring a selection of photographs from Angela
          Merkel. Devoid of any political intent, it is an iconographic testimony
          to the years in office of one of the most powerful women in the world.
        </p>
      </section>

      {/* Footer with gallery */}
      <section className={styles.footer}>
        <div className={styles.header}>
          <h1 className={styles.headerTitle}>
            Browse{" "}
            <span className={styles.mutti}>
              Mutti <sup className={styles.exposant}>beta</sup>
            </span>{" "}
            now
          </h1>
          <Link href="/categories">
            <button className={styles.goButton}>Go</button>
          </Link>
        </div>
        <div className={styles.gallery} ref={galleryRef}></div>
      </section>
    </main>
  );
}

"use client";

import { useEffect, useRef, useState, use } from "react";
import Link from "next/link";
import { items } from "@/data/items";
import styles from "./page.module.css";

const CATEGORY_META = {
  animal: {
    title: "Animal",
    heroImg:
      "https://media.vanityfair.fr/photos/6151dc113657cac85cbb2c43/16:9/w_2560%2Cc_limit/ABACA_781479_001.jpg",
  },
  food: {
    title: "Food & Beverage",
    heroImg:
      "https://img.buzzfeed.com/buzzfeed-static/static/2017-05/28/15/asset/buzzfeed-prod-fastlane-01/sub-buzz-4746-1496001576-2.jpg?downsize=800:*&output-format=auto&output-quality=auto",
  },
  vintage: {
    title: "Vintage",
    heroImg:
      "https://i.guim.co.uk/img/media/d465c37b95a9d60b9502ebb4874fc1f3fa775be6/246_24_2033_1219/master/2033.jpg?width=1200&height=1200&quality=85&auto=format&fit=crop&s=1060f80718168f29bccd9f9ca900ee0d",
  },
  technology: {
    title: "Technology",
    heroImg:
      "https://www.parismatch.com/lmnr/f/webp/r/1716,1144,000000,forcex,center-middle/img/var/pm/public/media/image/2022/03/18/02/Angela-Merkel-en-visite-au-Centre-des-astronautes-europeens-a-Cologne-le-18-mai-2016_7.jpg?VersionId=f65KXz4Py6hP7r2X0KtDT7bedccofc8a",
  },
  transport: {
    title: "Transport",
    heroImg: "https://static.dw.com/image/17156166_605.jpg",
  },
  sport: {
    title: "Sport",
    heroImg:
      "https://idsb.tmgrup.com.tr/ly/uploads/images/2021/09/24/thumbs/871x871/147271.jpg",
  },
};

export default function CategoryPage({ params }) {
  const { slug } = use(params);
  const galleryRef = useRef(null);
  const [lightbox, setLightbox] = useState(null);

  const meta = CATEGORY_META[slug];
  const categoryItems = items.filter((item) => item.category === slug);

  // Scroll-triggered reveal for gallery items
  useEffect(() => {
    if (!galleryRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add(styles.visible);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );

    const items = galleryRef.current.querySelectorAll(`.${styles.galleryItem}`);
    items.forEach((item, i) => {
      item.style.transitionDelay = `${(i % 3) * 0.1}s`;
      observer.observe(item);
    });

    return () => observer.disconnect();
  }, [slug]);

  // Close lightbox on Escape
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") setLightbox(null);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  if (!meta) {
    return (
      <div className={styles.empty}>
        <p>Category not found.</p>
        <Link href="/categories" className={styles.backLink}>
          <span className={styles.backArrow}>&larr;</span> Back to categories
        </Link>
      </div>
    );
  }

  return (
    <>
      {/* Hero */}
      <div className={styles.hero}>
        <img
          src={meta.heroImg}
          alt=""
          className={styles.heroImage}
          loading="eager"
        />
        <div className={styles.heroOverlay} />
        <div className={styles.heroContent}>
          <Link href="/categories" className={styles.backLink}>
            <span className={styles.backArrow}>&larr;</span> Categories
          </Link>
          <h1 className={styles.categoryTitle}>{meta.title}</h1>
          <p className={styles.photoCount}>
            {categoryItems.length} photograph{categoryItems.length !== 1 ? "s" : ""}
          </p>
        </div>
      </div>

      {/* Gallery */}
      <section className={styles.gallerySection}>
        {categoryItems.length === 0 ? (
          <p className={styles.empty}>Coming soon...</p>
        ) : (
          <div className={styles.gallery} ref={galleryRef}>
            {categoryItems.map((item) => (
              <div
                key={item.id}
                className={styles.galleryItem}
                onClick={() => setLightbox(item)}
              >
                <img
                  src={item.img}
                  alt={item.alt}
                  className={styles.galleryImg}
                  loading="lazy"
                />
                <div className={styles.caption}>
                  <p className={styles.captionTitle}>{item.legende}</p>
                  {item.place && (
                    <p className={styles.captionPlace}>{item.place}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Lightbox */}
      {lightbox && (
        <div className={styles.lightbox} onClick={() => setLightbox(null)}>
          <button className={styles.lightboxClose}>&times;</button>
          <img
            src={lightbox.img}
            alt={lightbox.alt}
            className={styles.lightboxImg}
            onClick={(e) => e.stopPropagation()}
          />
          <div className={styles.lightboxCaption}>
            <p className={styles.captionTitle}>{lightbox.legende}</p>
            {lightbox.place && (
              <p className={styles.captionPlace}>{lightbox.place}</p>
            )}
          </div>
        </div>
      )}
    </>
  );
}

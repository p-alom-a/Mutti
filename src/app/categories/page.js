"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import styles from "./page.module.css";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export default function Categories() {
  const cardContainerRef = useRef(null);

  useEffect(() => {
    const container = cardContainerRef.current;
    if (!container) return;

    gsap.registerPlugin(ScrollTrigger);

    const cards = container.children;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: container,
          start: "top 100%",
          end: "top 50%",
          scrub: 1,
        },
      });

      tl.from(cards[0], { x: -200, opacity: 0, duration: 5 });
      tl.from(cards[1], { x: 200, opacity: 0, duration: 5 });
      tl.from(cards[2], { x: -200, opacity: 0, duration: 5 });
      tl.from(cards[3], { x: 200, opacity: 0, duration: 5 });
      tl.from(cards[4], { x: -200, opacity: 0, duration: 5 });
      tl.from(cards[5], { x: 200, opacity: 0, duration: 5 });

      ScrollTrigger.refresh();
    });

    return () => ctx.revert();
  }, []);

  return (
    <>
      {/* Top banner */}
      <div className={styles.top}>
        <Link href="/">
          <img src="/icone-home.png" alt="Home" className={styles.btnHome} />
        </Link>
        <div className={styles.gradient}></div>
        <img
          src="https://i.guim.co.uk/img/media/57e1d2af0d048ed90976dd8873c266f64d57aec9/0_0_3500_2627/master/3500.jpg?width=700&quality=85&auto=format&fit=max&s=ddc7296cc4b27bc44f28499cc19c8a49"
          alt=""
          className={styles.topImg}
        />
      </div>

      {/* Hero */}
      <div className={styles.heroContainer}>
        <div className={styles.hero}>
          <h1 className={styles.heroTitle}>Categories</h1>
          <h3 className={styles.heroDescription}>
            Most of these photos were taken during official trips. Some are
            funny, others touching. All of them question the boundary between the
            public political persona and the person.
          </h3>
        </div>
      </div>

      {/* Categories cards */}
      <section className={styles.categories}>
        <div className={styles.cardContainer} ref={cardContainerRef}>
          <div className={`${styles.card} ${styles.one}`}>
            <h3 className={styles.cardTile}>Animal</h3>
          </div>
          <div className={`${styles.card} ${styles.two}`}>
            <h3 className={styles.cardTile}>Food&Beverage</h3>
          </div>
          <div className={`${styles.card} ${styles.three}`}>
            <h3 className={styles.cardTile}>Vintage</h3>
          </div>
          <div className={`${styles.card} ${styles.four}`}>
            <h3 className={styles.cardTile}>Technology</h3>
          </div>
          <div className={`${styles.card} ${styles.five}`}>
            <h3 className={styles.cardTile}>Transport</h3>
          </div>
          <div className={`${styles.card} ${styles.six}`}>
            <h3 className={styles.cardTile}>Sport</h3>
          </div>
        </div>
      </section>

      {/* Random */}
      <section className={styles.containerRandom}>
        <h1 className={styles.title}>Random</h1>
        <div className={styles.random}>
          <h3 className={styles.cardTile}>Discover the best of all categories</h3>
        </div>
      </section>
    </>
  );
}

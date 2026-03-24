"use client";

import Link from "next/link";
import styles from "./page.module.css";

export default function Categories() {

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
        <div className={styles.cardContainer}>
          <Link href="/categories/animal" className={`${styles.card} ${styles.one}`}>
            <h3 className={styles.cardTile}>Animal</h3>
          </Link>
          <Link href="/categories/food" className={`${styles.card} ${styles.two}`}>
            <h3 className={styles.cardTile}>Food&Beverage</h3>
          </Link>
          <Link href="/categories/vintage" className={`${styles.card} ${styles.three}`}>
            <h3 className={styles.cardTile}>Vintage</h3>
          </Link>
          <Link href="/categories/technology" className={`${styles.card} ${styles.four}`}>
            <h3 className={styles.cardTile}>Technology</h3>
          </Link>
          <Link href="/categories/transport" className={`${styles.card} ${styles.five}`}>
            <h3 className={styles.cardTile}>Transport</h3>
          </Link>
          <Link href="/categories/sport" className={`${styles.card} ${styles.six}`}>
            <h3 className={styles.cardTile}>Sport</h3>
          </Link>
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

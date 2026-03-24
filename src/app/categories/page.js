"use client";

import Link from "next/link";
import styles from "./page.module.css";

const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const CARDS = [
  { slug: "animal", label: "Animal", img: `${basePath}/galerieAnimal.png` },
  { slug: "food", label: "Food & Beverage", img: `${basePath}/galerieFood.png` },
  { slug: "vintage", label: "Vintage", img: `${basePath}/galerieVintage.png` },
  { slug: "technology", label: "Technology", img: "https://img.welt.de/img/politik/deutschland/mobile162881942/6822501957-ci102l-w1024/Deutschland-Besuch-Barack-Obama-3.jpg" },
  { slug: "transport", label: "Transport", img: "https://static.dw.com/image/17156166_605.jpg" },
  { slug: "sport", label: "Sport", img: "https://media.lesechos.com/api/v1/images/view/5bf181c53e45462cab4a21ae/1280x720/060160208421-web-tete.jpg" },
];

export default function Categories() {

  return (
    <>
      {/* Top banner */}
      <div className={styles.top}>
        <Link href="/">
          <img src={`${basePath}/icone-home.png`} alt="Home" className={styles.btnHome} />
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
          {CARDS.map((card) => (
            <Link
              key={card.slug}
              href={`/categories/${card.slug}`}
              className={styles.card}
              style={{ backgroundImage: `linear-gradient(to top, rgba(0,0,0,0.7) 5%, transparent 60%), url("${card.img}")` }}
            >
              <h3 className={styles.cardTile}>{card.label}</h3>
            </Link>
          ))}
        </div>
      </section>

      {/* Random */}
      <section className={styles.containerRandom}>
        <h1 className={styles.title}>Random</h1>
        <div
          className={styles.random}
          style={{ backgroundImage: `linear-gradient(to top, rgba(0,0,0,0.7) 2%, transparent 70%), url("${basePath}/random.png")` }}
        >
          <h3 className={styles.cardTile}>Discover the best of all categories</h3>
        </div>
      </section>
    </>
  );
}

const LOGOS = [
  { src: '/logos/alma.png', alt: 'Alma' },
  { src: '/logos/alter.png', alt: 'Alter' },
  { src: '/logos/bitpanda.png', alt: 'Bitpanda' },
  { src: '/logos/bnext.svg', alt: 'Bnext' },
  { src: '/logos/claap.png', alt: 'Claap' },
  { src: '/logos/cresta.png', alt: 'Cresta' },
  { src: '/logos/dapper-labs.png', alt: 'Dapper Labs' },
  { src: '/logos/deel.png', alt: 'Deel' },
  { src: '/logos/digbi-health.png', alt: 'Digbi Health' },
  { src: '/logos/evenflow.png', alt: 'Evenflow' },
  { src: '/logos/finmap.png', alt: 'Finmap' },
  { src: '/logos/gable.png', alt: 'Gable' },
  { src: '/logos/gigaml.png', alt: 'GigaML' },
  { src: '/logos/glassflow.png', alt: 'Glassflow' },
  { src: '/logos/grammarly.png', alt: 'Grammarly' },
  { src: '/logos/headout.png', alt: 'Headout' },
  { src: '/logos/hour-one.png', alt: 'Hour One' },
  { src: '/logos/jome.png', alt: 'Jome' },
  { src: '/logos/jump.png', alt: 'Jump' },
  { src: '/logos/klang-games.png', alt: 'Klang Games' },
  { src: '/logos/kobalt-labs.png', alt: 'Kobalt Labs' },
  { src: '/logos/leadbay.png', alt: 'Leadbay' },
  { src: '/logos/lemon-io.png', alt: 'Lemon.io' },
  { src: '/logos/libeo.png', alt: 'Libeo' },
  { src: '/logos/morado.png', alt: 'Morado' },
  { src: '/logos/omnea.png', alt: 'Omnea' },
  { src: '/logos/optaxe.png', alt: 'Optaxe' },
  { src: '/logos/oura.png', alt: 'Oura' },
  { src: '/logos/pandascore.png', alt: 'PandaScore' },
  { src: '/logos/preply.png', alt: 'Preply' },
  { src: '/logos/pipe.png', alt: 'Pipe' },
  { src: '/logos/playco.svg', alt: 'Playco' },
  { src: '/logos/playmint.png', alt: 'Playmint' },
  { src: '/logos/promethean.png', alt: 'Promethean' },
  { src: '/logos/prosper.png', alt: 'Prosper' },
  { src: '/logos/regression-games.png', alt: 'Regression Games' },
  { src: '/logos/rollstack.png', alt: 'Rollstack' },
  { src: '/logos/ten-little.png', alt: 'Ten Little' },
  { src: '/logos/the-games-agency.png', alt: 'The Games Agency' },
  { src: '/logos/toothio.png', alt: 'Toothio' },
  { src: '/logos/upstream.png', alt: 'Upstream' },
  { src: '/logos/vitract.png', alt: 'Vitract' },
]

export default function PortfolioTicker() {
  return (
    <div
      className="w-full overflow-hidden flex-shrink-0 py-3"
      style={{ backgroundColor: '#1400FF' }}
    >
      <div className="flex animate-ticker">
        {LOGOS.map((logo, i) => (
          <img
            key={`a-${i}`}
            src={logo.src}
            alt={logo.alt}
            className="h-6 w-auto mx-8 flex-shrink-0 opacity-80"
          />
        ))}
        {LOGOS.map((logo, i) => (
          <img
            key={`b-${i}`}
            src={logo.src}
            alt={logo.alt}
            className="h-6 w-auto mx-8 flex-shrink-0 opacity-80"
          />
        ))}
      </div>
    </div>
  )
}

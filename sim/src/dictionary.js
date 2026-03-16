// Common English dictionary for spell checking (~5000 words)
// Compact representation: space-separated words split into a Set
// Includes common programming and tutorial vocabulary

const WORDS = `
a ab able about above absent accept access account across act action active actual add added
address admit adult advance advice affect afford after again against age aged agent ago agree
ahead aid aim air all allow almost alone along already also alter always am among amount an
ancient and anger angle angry animal announce annual another answer any anyone anything anyway
apart appeal appear apple apply approach appropriate area argue arm army around arrange arrest
arrive art article as ask asleep associate assume at attack attempt attention attract audience
author automatic available average avoid awake aware away awful
back background bad badly bag balance ball ban band bank bar bare base basic basis bat bath
battle be bear beat beautiful beauty because become bed bedroom beer before began begin beginning
behind being belief believe bell belong below bend beneath benefit beside best better between
beyond big bill bind bird birth bit bite black blade blame blank blind block blood blow blue
board boat body bomb bond bone book border born borrow boss both bother bottle bottom bound box
boy brain branch brave bread break breakfast breath breathe brick bridge brief bright bring
broad broke broken brother brown brush build building burn burst bus business busy but butter
button buy by
call calm came camera camp campaign can cap capable capital captain capture car card care career
careful carefully carry case cash cast cat catch category cause cell center central certain chain
chair chairman challenge chance change channel chapter character charge charity chart chase cheap
check cheese chest chief child choice choose church circle citizen city civil claim class clean
clear clearly client climb clock close closely clothes club coach coal code coffee cold collapse
colleague collect collection college color column combination combine come comfort command comment
commercial commission commit committee common communicate community company compare competition
complete complex computer concentrate concept concern condition conduct conference confidence
confirm conflict congress connect connection conscious consider contain content context continue
contract contrast contribute control conversation cook cool copy core corner correct cost could
council count country county couple course court cover crack crash create creation credit crew
crime criminal crisis critical cross crowd cry cultural culture cup current currently curve
customer cut cycle
dad damage dance danger dangerous dare dark data database date daughter day dead deal dear death
debate debt decade decide decision declare decline deep deeply defeat defend define definitely
degree delay deliver demand democracy democratic department depend deposit describe design
designer desire desk despite destroy detail determine develop development device devote dialogue
die diet difference different difficult difficulty dig digital dinner direct direction directly
director disappear discipline discover discussion disease dismiss display distance district
divide division do doctor document dog dollar domestic door double doubt down downtown dozen draft
drag drama dramatic draw dream dress drink drive drop drug dry due during dust duty
each ear early earn earth ease easily east eastern easy eat economic economy edge edition editor
education effect effective effectively effort eight either elderly election electric element
eliminate else elsewhere emergency emotion emotional emphasis empire employ employee employer empty
enable encourage end enemy energy engage engine engineer enjoy enormous enough ensure enter
entire entirely entrance entry environment equal equally equipment era error escape especially
essay essential essentially establish estate estimate evaluate even evening event eventually ever
every everybody everyday everyone everything everywhere evidence evil evolution evolve exact
exactly examine example exceed excellent except exchange exciting executive exercise exhibit exist
existence existing expand expect expectation expense expensive experience experiment expert
explain explanation explicit explore explosion expose exposure extend extension extensive extent
external extra extraordinary extreme eye
face facility fact factor fail failure fair fairly faith fall familiar family famous fan far farm
farmer fashion fast fat fate father fault favorite fear feature federal fee feed feel feeling
fellow felt female fence few fewer fiction field fifteen fifth fifty fight figure file fill film
final finally finance financial find finding fine finger finish fire firm first fish fit five fix
flag flat flight float floor flow flower fly focus folk follow food foot for force foreign
forest forever forget form formal former fortune forward found foundation four frame framework
free freedom french frequency frequent frequently fresh friend front fruit fuel full fully fund
fundamental funny future
gain galaxy game garden gas gate gather gave general generally generate generation gentle
gentleman get giant gift girl give given glad glass global go goal god gold golden gone good
government grab grade gradually grand grandfather grandmother grant grass gray great greatest
green grew ground group grow growing growth guarantee guard guess guest guide guilty gun guy
habit hair half hall hand handle hang happen happy hard hardly hat hate have he head health
healthy hear heard heart heat heavy height hell hello help helpful her here herself hi hide high
highlight highly hill him himself hip hire his historian historic historical history hit hold hole
holiday home honestly hope horse hospital host hot hotel hour house household housing how however
huge human humor hundred hungry hurt husband
idea identify if ignore ill illegal image imagine immediate immediately impact implement
implication imply importance important impose impossible impress impression impressive improve
improvement in incident include including income increase increasingly incredible incredibly
indeed independence independent index indian indicate individual industrial industry infant
influence inform information initial initially injury inner innocent input inquiry inside insist
install instance instead institution insurance intellectual intelligence intend intention interest
interested interesting internal international internet interpret intervention interview into
introduce introduction invasion invest investigate investigation investigator investment investor
invitation involve iron island issue it item its itself
jacket jam jar jew job join joint joke journal journalist journey joy judge judgment juice jump
junior jury just justice justify
keen keep key kick kid kill kind king kiss kit kitchen knee knew knife knock know knowledge known
lab label lack lady lake land landscape language large largely laser last late lately later
latter laugh launch law lawn lawyer lay layer lead leader leadership lean learn learning least
leather leave left leg legal legend legislation lend length less lesson let letter level library
life lift light like likely limit line link lip list listen literally literary literature little
live living load loan local locate location lock long look lord lose loss lost lot loud love
lovely lover low lower luck lunch lung
machine mad magazine mail main mainly maintain major majority make male mall man manage
management manager manner many map margin mark market marriage married marry mask mass massive
master match material math matter may maybe me meal mean meaning measure measurement meat media
medical meet meeting member membership memory mental mention merely mess message method middle
might military milk million mind mine minister minor minority minute mirror miss mission mistake
mix mixture mode model moderate modern modest mom moment money monitor month mood moon moral more
moreover morning most mostly mother motion mount mountain mouse mouth move movement movie much
multiple murder muscle museum music musical must mutual my myself mystery myth
naked name narrative narrow nation national natural naturally nature near nearby nearly
necessarily necessary neck need negative negotiate negotiation neighbor neither nerve nervous
network never nevertheless new newly news newspaper next nice night nine no nobody nod noise none
nor normal normally north northern nose not note nothing notice notion novel now nowhere number
numerous nurse nut
object objection objective obligation observation observe obtain obvious obviously occasion
occasionally occur odd odds of off offense offensive offer office officer official often oh oil
ok old on once one ongoing online only onto open opening operate operation operator opinion
opponent opportunity oppose opposite opposition option or orange order ordinary organic
organization organize orientation origin original other otherwise ought our ourselves out outcome
outside overcome overlook owe own owner
pace pack package page paid pain paint painting pair pale palm pan panel pant paper parent park
parking part partially particular particularly partly partner party pass passage passenger past
path patience patient pattern pause pay payment peace peak peer penalty people per percent
percentage perfect perfectly perform performance perhaps period permanent permission permit
person personal personally perspective phase philosophy phone photo phrase physical pick picture
piece pile pilot pink pipe pitch place plan plane plant plate platform play player please
pleasure plenty plus pocket poem poet poetry point pole police policy political politician
politics pollution pool poor poorly pop popular population porch port portion portrait position
positive possibility possible possibly post pot potato potential potentially pound pour poverty
power powerful practical practice pray prayer precisely predict prefer preparation prepare
presence present presentation preserve presidency president presidential press pressure
presumably pretty prevent previous previously price primarily primary prime principal principle
print prior priority prison prisoner privacy private probably problem procedure proceed process
produce producer product production profession professional professor profile profit program
progress project promise promote proof proper properly property proportion proposal propose
proposed prosecutor prospect protect protection protein protest prove provide provider province
provision psychological psychologist psychology public publication publicly publish pull punch
purchase pure purple purpose pursue push put
qualify quality quarter quarterback queen question quick quickly quiet quietly quit quite quote
race racial racism racist radio rage rain raise range rank rapid rapidly rare rarely rate rather
rating reach react reaction read reader reading ready real realistic reality realize really
reason reasonable rebel recall receive recent recently recognition recognize recommend
recommendation record recover recovery recruit red reduce reduction refer reference reflect
reform refrigerator refuse regard regarding region regional register regular regulation reinforce
reject relate relation relationship relative relatively release relevant relief religion
religious reluctant rely remain remaining remarkable remember remind remote remove repeat
repeatedly replace reply report reporter represent representation representative republic
republican reputation request require requirement research researcher resident resist resistance
resolution resolve resort resource respond response responsibility responsible rest restaurant
restore restriction result retain retire retirement return reveal revenue review revolution rhythm
rich rid ride rifle right ring rise risk river road rock role roll romantic roof room root rope
rose rough roughly round route row rule run running rural rush
sacred sacrifice sad safe safety sake salad salary sale salt same sample sanction sand satellite
satisfaction satisfy save saving say scale scandal scene schedule scholar scholarship school
science scientific scientist scope score screen sea search season seat second secondary secret
secretary section sector secure security seek seem segment seize select selection self sell senate
senator send senior sense sensitive sentence separate sequence series serious seriously serve
service session set setting settle settlement seven several severe shake shall shape share sharp
she shed sheer shelf shell shelter shift shine ship shirt shock shoot shooting shop shopping shore
short shortage shortly shot should shoulder shout show shower shut shut side sight sign signal
significance significant significantly silence silent silver similar similarly simple simply
simultaneously since sing singer single sir sister sit site situation six size ski skill skin sky
slave slavery sleep slice slide slight slightly slim slip slow slowly small smart smell smile
smoke smooth snap so so-called soccer social society soft software soil solar soldier solid
solution solve some somebody someday somehow someone something sometimes somewhat somewhere son
song soon sophisticated sorry sort soul sound source south southeast southern space speak speaker
special specialist species specific specifically speech speed spend spirit spiritual split
spokesman sport spot spread spring square squeeze stability stable staff stage stair stake stand
standard standing star stare start state statement station status stay steady steal steam steel
step stick still stock stomach stone stop store storm story straight strange stranger strategic
strategy stream street strength stress stretch strike string strip stroke strong strongly
structure struggle student studio study stuff stupid style subject submit subsequent substance
substantial succeed success successful successfully such suddenly suffer sufficient sugar suggest
suggestion suit summer sun super supply support supporter suppose sure surely surface surgery
surprise surprised surprising surprisingly surround surrounding survey survival survive suspect
suspend suspicion sustain sweep sweet swim swing switch symbol symptom system
table tactic tail take tale talent talk tank tap tape target task tax taxpayer tea teach teacher
teaching team tear technology television tell temperature temporary ten tend tendency term terms
terrible test testimony testing text than thank that the theater their them theme themselves
then theory therapy there therefore these they thick thin thing think thinking third thirty this
those though thought thousand threat threaten three throat throughout throw thus ticket tie tight
time tiny tip tire tired title to today toe together tomorrow tone tonight too tool top topic
toss total totally touch tough tour tourist tournament toward towards tower town toy trace track
trade tradition traditional traffic trail train training trait transfer transform transition
translate transportation travel treat treatment tree trend trial trick trip troop trouble truck
true truly trust truth try tube tunnel turn tv twelve twenty twice twin two type typical
typically
ugly ultimate ultimately unable uncle under undergo understand understanding unemployment
unfair unfortunately unhappy uniform unify union unique unit united universal universe
university unknown unless unlike unlikely until up upon upper upset urban urge us use used
useful user usual usually utility
vacation valley valuable value variable variation variety various vary vast version very veteran
via victim victory video view viewer village violation violence virtual virtually vision visit
visitor visual vital voice volume volunteer vote voter vs vulnerable
wage wait wake walk wall want war warm warn warning wash waste watch water wave way we weak
weakness wealth weapon wear weather web website wedding week weekend weigh weight welcome welfare
well west western wet what whatever wheel when whenever where whereas wherever whether which while
whisper white who whole whom whose why wide widely widespread wife wild will willing win wind
window wine wing winner winter wire wisdom wise wish with withdraw without witness woman wonder
wonderful wood wooden word work worker working works world worry worse worst worth worthy would
wound wrap write writer writing wrong
yard yeah year yell yellow yes yesterday yet yield you young youngster your yourself youth zone
`.trim();

// Programming, tech, and tutorial-specific vocabulary
const TECH_WORDS = `
abstract algorithm align allocate alpha annotation api append application argument array assert
assertion assign assignment async attribute authentication authorization await
backend bash beta binary bit bitwise boolean branch breakpoint browser buffer bug build bundle
byte bytecode
cache callback capitalize cast changelog char character checkpoint class cleanup cli client
clipboard clone closure cmd coerce column command comment commit compile compiler component
compose concat concatenate conditional config configuration configure connection console
constant constructor container controller convert cookie counter cron crud css cursor
daemon data database datatype debug debugger declaration declare decrement decrypt default
defer define definition delete demo dependency deploy deployment deprecated deprecation
dereference descriptor deserialize destructor dev developer dictionary diff directory disable
dispatch dispose distribution docker dom domain driver dropdown duplicate dynamic dynamically
echo element emit emitter encapsulate encode encrypt endpoint engine enum enumeration
environment equals error eval evaluate event exception exec executable execute exit export
expression extend extends extension extract
facade factory fallback fallthrough fetch field file filename filesystem filter finally
flag flatten float flush folder font footer fork format formatter framework frontend func
function functional
garbage gateway generate generator generic getter git github glob global goto gpu gradient graph
grep gui guid
handler hash hashmap hashtable header heap hello hex hexadecimal hook hostname html http https
icon identifier idle iframe ignore immutable implement implementation import indent indentation
index inherit inheritance init initialize injection inline inner input insert inspect instance
instantiate integer integrate integration interactive interface internal interpolate interpreter
interrupt io iterate iterator
java javascript job join json junit
kernel key keymap keypress keystroke keyword kotlin
lambda layout lazy lib library lifecycle link lint linter linux list listener literal load loader
localhost log logger logging logic login logout lookup loop lowercase
macro main malloc manifest map mapping markdown markup matcher memo memoize memory merge metadata
method middleware migrate migration minimal mixin mock modal mode modifier module monorepo mount
multiline multithread mutex
namespace native navigate navigation nest nested network nil node normalize notation null
nullable
oauth object observable observe offset opaque opcode operand operation operator optimize option
optional oracle order os output overflow overload override
package padding parallel parameter parent parse parser partial pass password patch path pattern
payload peer pending performance permission persist pipeline pixel placeholder platform plugin
pointer poll polymorphism pool popup port portal postfix prefix print printf priority private
process production profile profiler program promise prompt property protocol prototype provider
proxy pseudo public pull push
query queue
race readonly realtime recursion recursive redirect redux refactor reference regex regexp
registry release reload remote render renderer repo repository request resolve response rest
restore retry return revert rollback root router routing ruby run runtime rust
sandbox save scalar scaffold schema scope screenshot script scroll sdk search seed select
selector semantic semaphore sequence serial serialization serialize server service session setter
setup shader shadow shallow shell shift signal signature simulate simulation singleton size
slice snippet socket software sort source span spawn spec specification split sql sqlite ssh
stable stack standalone startup state static status stderr stdin stdout storage store stream
strict string strip struct structure stub style subclass submodule subroutine subscribe subset
suffix suite super superclass suppress svg swap switch sync synchronize synchronous syntax
system
tab tag task tcp template terminal test testing text textarea thread throttle throw timestamp
tls todo toggle token toolbar tooltip top trace track trait transaction tree trigger trim true
truncate tuple type typedef typescript
udp ui uint undefined underline underscore unicode union unittest unix unset unsigned unwrap
update upgrade upload uppercase uri url user utf utf8 util utility
validate validation value var variable vector verbose version viewport vim virtual visible
visual void
warning watch web webpack webserver websocket widget width wiki wildcard window wizard word
worker workflow workspace wrapper write
xml xor
yaml
zero zip zoom
`.trim();

// Additional common English words to expand coverage
const MORE_WORDS = `
abandon ability absence absolute absorb abuse academic acceptable acceptance accessible
accommodate accompany accomplish accordance accountant accounting accumulate accuracy accurate
accusation accuse accused accustom ache achieve achievement acid acknowledge acquaint acquire
acquisition acre activate actively activist activity actor actress actual adapt adaptation
additional adequate adjust adjustment administration administrative administrator admire
admission adolescent adopt adoption advancement adventure advertising advocate affection
affordable african afternoon agenda aggressive aging agreement agricultural agriculture ahead
aircraft airline airport alarm album alcohol alien alignment allegation alliance allied
allocation alongside alternative aluminum amateur ambassador ambition ambitious amendment
amid analysis analyst analyze ancestor ancient angel animation ankle anniversary announce
announcement annoy annual anonymous anxiety anxious anybody anyhow anymore apartment apology
app apparatus apparent apparently appetite applaud applicant application appoint appointment
appreciation apprentice appropriately approval approve approximate arab architect architecture
arena arise arithmetic armed arrow artificial aside asleep aspect assault assemble assembly
assertion asset assignment assist assistance assistant associate association assumption assurance
assure athlete athletic atmosphere attach attachment attain attempted attendance attractive
attribute auction aunt authentic auto automobile automotive availability avenue awesome
baby backup bacteria badge badly balanced ballet ban banana bandwidth bare barely bargain barrel
barrier basement bat batch beam bean beast behalf behave behavior beloved belt bench benchmark
bend beneath beneficial berry beside bet beverage bias bicycle bid billion biography biological
biology bishop bizarre blade blank blanket blast bleed bless blessing blind blonde bloom
blow bonus boom boot border boring boss bounce boundary bow bowl boyfriend brake breast
breed brick briefly brilliant broad broadcast broadly broken bronze bubble buck budget
builder bulk bullet burden bureaucracy burial buyer
cabin cabinet cable calendar calm camera campaign campus canadian candidate capability capacity
carbon careful carrier casino casual catalog catalogue catastrophe catholic caution ceiling
celebrate celebration celebrity cemetery ceremony certainty chain chairman championship chaos
characterize charity chef chemical chemistry childhood chin chip chocolate chronic chunk
circuit circumstance citation cite civilian civilization claim clarify clarity classroom
clean click cliff climate clinical clip closely clothing clue cluster coalition cognitive
coincidence cold colleague collective colonial colony combination comfort comic commander
commemorate commentary committee commodity communicate companion comparable compatible compelling
compensate compensation competence competitive complaint complement complexity compliance
complicate comprehensive comprise compromise compute conceive concentrate conception
congressional connect consciousness consensus consequence conservation conservative
considerable consistently conspiracy constitute constitutional construct consult consultant
consumption contemporary contempt contest continent conventional conversion convey conviction
convince cooperation coordinate coordinator cop cope corner corporate correction correlation
correspondent corridor corruption cottage counsel counter counterpart countryside courage
courtesy coverage craft crash creative credibility crew criterion criticism crop crucial crystal
curiosity curious currency curriculum curtain custody cute
dairy dam damn dare darkness data dawn deadline dealer dear debate decent deck decoration decrease
defeat deficit define delay delegate delegation deliberately democratic demonstrate demon denial
density depart departure dependent depict deployment depression deprive deputy derive descent
deserve desktop desperate destruction detail detect detective determination devil devote diamond
diary dictate dictionary diet differential dignity dimension dip diplomatic disability disaster
disclose discount discourse discrimination disorder disposal dispose dispute distant distinct
distinction distinguish distribute disturb diverse diversity divorce doctrine documentation
domain domestic dominant dominate donor dose double downtown draft drain dramatic dramatically
drawing drift drinking driving drought dry dual duke dump duration dust dynamic dynasty
eager earning ease echo ecological economic economics ecosystem editorial educate educator
effectiveness efficiency effort eighth elaborate electric electrical electronics elegant
eligible elimination elite embrace emission emotional emperor empire enable encounter
endless endorse enforcement engagement enormous enterprise entertainment enthusiasm entity
entrance entrepreneur envelope environmental epidemic equation equip equivalent era essay
essence essentially establishment ethic evaluate eventually evil evolution examination
examine exceptional excess excessive excited excitement exclusive execute exhibition exile
expansion expedition expenditure experiment experimental exploitation explosion export
exposure extension extensive extraordinary extreme
fabric facilitate fade failure fairy fame famous fantastic fantasy fascinating fatal
fate favorable feast federal federation feedback feminist fence festival fiber fiction
fierce fighter filing final fiscal fishing flag flame flexibility flip float flood
footage forecast foreigner formula forth fortune fossil foster foundation founder fraction
fragment franchise frankly fraud freight frequent friendship frost frustration fulfill
fundamental fundraising furthermore fury fusion
gallery gambling gang gap gasoline gather gaze gear gender generous genetic genius genre
genuine gesture ghost giant given glad glance glimpse globe glory golden golf gorgeous
govern governor gradually grain grand grandfather graphic grasp grave greatly greenhouse
greet grief grin grip grocery gross ground guarantee guardian guidance guilty gut
habitat halfway handful handsome harbor hardware harmony harsh harvest hat haven
headquarters healing heat helpful heritage hero hide high highly hint historic
historian hobby hollow homework honey honor horrible horizon hostile hostage household
housing humor hunt hurricane hydrogen hypothesis
ideal identical identification illness illustration imagination immune implementation
imprisonment incentive inch incidence incident incorporate incredible index indicate
indication indigenous indirect inevitable inflation infrastructure ingredient inhabitant
initially initiative injury innovation innovative input insert insight inspection
inspiration installation institutional instructor instrument insurance intellectual
intelligence intense intensity interaction interior interpretation intervention intimate
introduction invade invasion inventory investment invisible invitation involvement isolation
jacket journal joy judicial juice junction junior jury justification juvenile
keen keyboard kingdom knee
label laboratory landscape largely laser lasting launch lawn layout league lean legend
legislative legitimate leisure length lesser liberal liberation liberty lieutenant lifestyle
lifetime likelihood likewise limitation literacy literally logical lonely longtime loose
lot lottery lovely loyal luck luxury
magic magical mainland mainstream maker makeup mandate manifest manipulation manor margin
marine marker marketplace mask mathematics mature meaning meaningful mechanism medication
medium membership mental mere merge merit metaphor migration mild mineral minimal minimum
ministry minority miracle mirror misery missile mission mixture mobile mode modest
momentum monitor monthly monument mortgage motion motivate motivation mount mountain
multiple municipal murder mystery
narrative nasty nationwide navigate necessity neighborhood nervous newsletter nightmare
noble nomination nominee nonetheless nonprofit northeast notion nowhere numerous nutrition
o obstacle occasional occupation occupy offense offensive offering officially offspring ongoing
online openly opening operational opponent optical optimistic option oral orange organic
orientation outdoor output outreach outstanding overcome overseas overwhelming ownership
painful pale panic parallel parental participation partnership passage passenger passion
passive patience patrol patron pause peak peasant penalty pension perceive percent
percentage permanent permanently personally personally persuade petition phenomenon
philosopher philosophy photograph photography phrase physician piano pile pilot pitch
placement planet plantation plead pledge plot plug plus poet pole politic popularity
portion portrait pose possess possession poster postpone pot pottery pound practitioner
pray prayer precious precisely prediction predominantly preference pregnancy prejudice
preliminary premier premise premium prescription previously pride priest primarily
primitive principal print prisoner privilege probe productive profession professor profound
prominent proposal prosecution prospective prosperity protein provider province provoke
psychiatric publication punish punishment pursuit puzzle
qualification quarterly quest
racial radiation radical rage railroad rainbow rally rapid reach react readily
realistic realm rear reasonable recession recipe recognition recommendation reconstruction
recover recovery recreational recruit reform refugee regardless regime regional register
regulate rehabilitation reign rejection relate remarkable remedy removal repair repeated
replacement reproduce reproductive republic researcher reservation residential resignation
resist resistant resolve respective respectively respond restoration restriction resume
retirement revenue reverse reviewer revolution revolutionary rhythm rid rifle rigid ritual
rival robot robust rocket romantic rope rotation rough routine royal rumor running
saint sake sand satellite satisfied saving scenario scholarship scientific scope seasonal
secondary sector seemingly selective senator sensitive separately sequence servant sexual
shadow shallow shape shed sheer shelter shield shipping shock shore shortage shortly
shoulder signature significance silent silly simultaneously sink situated sketch skilled
skip slavery slim slow snap solely solid solution somewhat sophisticated soul southern
span spare specialist spectacular spectrum sphere spiritual sponsor spouse squeeze
stability stable stadium stake stance standing startup steady steep stem stereotype
stimulus stir storm strategic strengthen strictly strip structural studio submission
submit subsidiary substance substantial succeed suicide suitable summit sunlight super
supplement supportive supreme surface surgery surplus surprisingly surveillance suspect
suspend suspicion sustainable sweep sword symbol sympathy syndrome
tablet tactic tail tale talent tap tape target taxpayer teammate temporarily tender
tenure terminal territory terror terrorist testify testing thankfully theater theme
therapy thereby thesis thick thigh thoroughly thoughtful threshold throne tide timber
tissue tobacco tolerance tolerate tomorrow tongue torture total tournament trace trader
trading tragedy trail trait transaction transformation transition transmission
transparent transportation trauma tremendous trend tribe trick trigger triumph troop
tropical trouble truly trustee tuition tumor tunnel twin twist
ugly undergo underlying unemployment unfair uniform unite unity universal universe unknown
unlikely unprecedented unstable unusual upcoming upgrade upper urban utility
vacation valid variation venture venue verbal verdict version versus viable victory
viewpoint violation virtual virtually vocabulary volunteer
wage wander warn warranty warrior waste weaken weakness wealthy weapon weekly weigh
weird welfare wheat whereas wherever whisper widespread willing wind withdraw withdrawal
witness wooden workforce workshop worldwide worship worthwhile worthy wound
`.trim();

// Extra common words: verb forms, articles, pronouns, prepositions, conjunctions, everyday words
const COMMON_EXTRAS = `
am an are as at be been being by did do does doing done down each for from get gets getting
giving go goes going gone got had has have having he her hers herself him himself his how
if in into is it its itself just know known let like made make makes making many me might
more most much must my myself neither no nor not now of off often oh ok on one only or
other others our ours ourselves out over own per put quite ran really run said same saw
say says see seen shall she should since so some someone something sometimes still such
take taken tell than that their theirs them themselves then there these they this those
through thus till to too toward towards two under unless until unto upon us used using
very via want wanted wants was we went were what whatever when where whether which while
who whom whose why will with within without won would yes yet you your yours yourself
able add ago air also always another ask asked away back bad began begin being best big
black blue body book both boy brought call came can cannot car case certain children city
close cold coming day days did different doesn door during early end enough even every
eyes face family far feel feet felt few find first five food form found four gave girl go
going good great group hand hands head hear help here high home house however hundred idea
important john keep kind knew land large last left let life line little live long look
looking lost made man may men mind money morning mother move mr mrs much must name need
never new next night nothing now number off often old one only open order own part past
people perhaps place point put quite read rest right room run said same saw school
second seem set several shall show side since small something sometimes soon stand start
state still stood story such sure table tell than these thing think thought three time
today told too took turn two under united until use very walk water way well what white
whole why without woman women won word work world would write year young
`.trim();

// Additional common words that appear in programming tutorials and documentation
const TUTORIAL_WORDS = `
above accordingly actual additionally afterwards albeit allows alongside altogether amidst
analogous another anybody anything anywhere apparently applies applying appropriate
approximately aside assuming availability
basically becomes beginning belongs beside besides beyond briefly broadly
carefully centrally certainly characteristically closely commonly comparatively completely
conceptually consequently considerably consistently continuously conversely correctly
correspondingly critically crucially
decidedly deeply deliberately differently distinctly
effectively efficiently elegantly elsewhere entirely equally especially essentially eventually
evidently exactly exclusively explicitly extensively externally extraordinarily
fairly familiarly feasibly finally firstly flexibly formerly fortunately frequently
fundamentally
generally genuinely globally gracefully gradually
hence hereafter herein highly historically hopefully however hypothetically
ideally identically illustrate immediately importantly incidentally independently individually
informally inherently initially innovatively instantly intensively internally intuitively
inversely
largely lately legitimately likewise locally logically loosely
mainly manually meaningfully meanwhile mechanically methodically minimally moderately mostly
namely nationally naturally negatively nevertheless nominally normally notably
objectively obligatorily occasionally officially operationally optimally ordinarily originally
outwardly overall
paradoxically partially particularly passively perfectly periodically permanently personally
physically plainly plausibly politically poorly positively possibly potentially practically
precisely predictably predominantly preferably presently presumably previously primarily
principally privately proactively probably productively professionally profoundly progressively
prominently promptly properly proportionally prospectively purely purposefully
quantitatively quarterly quickly quietly
randomly rapidly readily realistically reasonably recently recursively redundantly regularly
relatively reliably remarkably remotely repeatedly reportedly reproducibly respectively
responsibly retroactively rigorously robustly routinely
satisfactorily seamlessly secondly securely selectively separately sequentially seriously
significantly similarly simplistically simultaneously skeptically slightly socially solely
somewhat specifically sporadically steadily strategically strictly structurally subsequently
substantially successfully sufficiently superficially supposedly surely surprisingly
symmetrically syntactically systematically
tangibly technically temporarily tentatively theoretically thereby therefore thoroughly thus
traditionally transparently tremendously trivially truly typically
ubiquitously ultimately unanimously unconditionally understandably undoubtedly unfortunately
uniformly uniquely universally unmistakably unnecessarily unofficially unquestionably
unreliably until usefully usually
vaguely validly variably verbosely verifiably vertically vigorously virtually visually vitally
voluntarily
whatsoever whenever wherever wholly widely willingly worthwhile
`.trim();

// Merge all word lists into a single Set (duplicates automatically removed)
// Supplementary common words to fill gaps
const SUPPLEMENTARY = `
ab abs accordingly additionally ads affordable afterwards albeit align alongside altogether
amidst analogous api apps are aren arose as assign assuming availability
bandwidth basically bean been belongs beside besides blank boolean boot brightness broadly
capability catalog centre checkbox clicked clipboard codebase coding cognitive collaborative
combo computational configured connectivity const consulting container conversely
cookie coordinate coordinates css customizable
dashboard dataset datasets debug demo didn dir doc docs doesn download downloadable dropdown
each earned edit editable efficiently email embed emoji endpoint endpoints enrollment
enum err exam faq favicon feedback filesystem finalize flex footer formatted formatting
framework frontend fullscreen func
git gradle graphical gui guid
had has homepage hotkey html href http
icon ids iframe imported inbox inline inputs installable integer io
javascript json jsx
kotlin
lang layout lib lifecycle linux localhost login logout lorem lowercase
mac malloc markup max merged metadata middleware min modal monospace multiline
namespace navbar nested npm null nullable
onboard onboarding onclick opaque optimize org os outage overflow
param params permalink php placeholder plugin png popup postgres preset preview prod
profiler programmatically progressbar proto providers provisioning
readme realtime rect refactoring regex relaunch renderer repo reusable runtime
scalable schema screenshot sdk serialized sidebar signup snippet spam sql src ssh startup
statusbar stdin stdout stylesheet subclass substring svg sync
tab tcp template terminal textarea timestamp todo tooltip tsx tutorial typescript
ui undo unicode unix unset uploading uppercase uri url username util uuid
viewport vim vue
was web websocket weren wifi wiki workflow workspace
xhtml xml
yaml yml
zip

about above accept across actually after again ago agree almost along already although
among answer anything area ask ate beautiful because before began begin behind believe below
between beyond billion board born bought brought build built business buy call cannot carry
catch caught center change child class clear close cold color come common contain continue
correct country course cross current dark deep develop direction discover draw drive early
eat effect either else energy enjoy even evening ever example exercise explain express fact
fall far fast father feel field figure fill final fine fly follow force found free friend
front full garden general give glad gone govern grew grow guess happen happy hear heart
heavy herself himself hold hot house huge human hurry ill include increase indicate inside
interest itself job join joy jump keep key kill knew large later laugh law lay lead learn
leave less letter lie likely line list listen live long lose low machine main major mark
material matter measure meet million mind miss modern moment month morning move much music
nation nature necessary need never news none north notice number offer office often once
open opportunity order outside page paper parent particular party pattern pay period person
pick picture place plan play please point poor position possible present press pretty
problem produce product program project property prove provide public pull question quick
race raise range rather reach read receive record red remember report require result rich
right rise road rock rule safe sat scene sea season sell send serve set share short simple
since sit size small social sort south speak special spend stand star start stay stop
story street strong student study succeed suggest support suppose table talk teach team
tell ten test think thought thus together tonight touch toward travel tree true turn
type understand unit upon voice wait walk war watch white wide win wish wonder word
worker wrong wrote young

advanced beginner challenge comprehensive comprehensive concept configure demonstrate
documentation efficiently essential everyday familiar feature fundamentals guide
helpful illustrate implement important initialize instruction intermediate introduce
keypress keybinding keyboard level master method navigate overview parameter powerful
principle productive programming reference relevant resource review section setup
shortcut simplify solution strategy summary technique tips tricks understand useful
walkthrough worksheet

absorbing abstract acceleration accessible accomplishment accurately acquiring activation
adapter adequately adjacent adjustable administrator admirable admittedly adopting advancing
advantageous aggregate aggressively alert allocating amazingly ambitious amplify amusing
angular annotated announcement anticipate appealing applicable appreciation arbitrary array
articulate assessing assessment attachment attempting authenticate automatically awareness
backbone bandwidth baseline beautifully behaving beneficial binding blocking bookmarking
bootstrap boundary briefly broadening browsing bug bundling bypassing
caching calculating capability capturing carefully centralized certified challenging
changelog checking chrome circumstance clarity clickable cloning coercion collaboration
column combining command commenting communication compactly comparative compatibility compiler
completing component composing comprehensive computing concern concurrency configurable
conjunction consistently constructing container contextual contributing conversion converting
coordinating correcting corresponding creating creatively css customization
database debugging declaring deeply default defining delegation deleting dependency deploying
deprecating describing designing detailed detecting developer diagnostic dialog dimensioning
directing disabling discovering displaying distinguishing distributing dockerizing documenting
downloading dragging dropping duplicating dynamically
editing efficiently embedding emergency emitting enabling encoding ending enforcing enhancing
ensuring entity enumerating equipping erasing escaping establishing estimating evaluating
eventually examining exceeding exception exchanging excluding executing exemplifying exhibiting
expanding expecting experimenting exploring exposing expressing extracting
facilitating factoring featuring fetching filtering finalized fixing floating flowing focusing
foolproof forcing forecasting formatting forwarding fragmenting frequently fulfilling
gathering generating globally governing gradually graphing grouping guaranteeing guarding
handling hashing heading helping highlighting hooking hosting hovering
identifying ignoring illustrating imagining immediately implementing importing improving
including incorporating increasing independently indexing indicating individually inferring
informing inheriting initializing injecting innovating inserting inspecting installing
instantiating instructing integrating intelligently intending interacting intercepting
interfacing internally interpolating interpreting introducing invalidating investigating invoking
isolating iterating
joining jumping justifying
labeling launching layering leveraging licensing limiting linking listing loading locally
locking logging looping
maintaining managing manipulating mapping matching maximizing measuring merging messaging
migrating minimizing mocking modeling modifying monitoring mounting moving multiplying mutating
naming natively navigating nesting networking neutralizing normalizing notifying
observing obtaining occurring offsetting omitting opening operating optimizing ordering
organizing orienting outputting overflowing overriding
packaging padding pairing parallelizing parameterizing parsing partitioning passing patching
pausing pending performing permitting persisting piping planning plugging pointing polling
populating porting positioning posting prefixing preprocessing presenting preventing
prioritizing processing producing profiling programming projecting promising promoting
prompting propagating protecting prototyping providing proxying publishing pulling pushing
qualifying querying queuing
ranging reaching reading rebasing rebuilding receiving recognizing recommending reconciling
recording recovering redirecting reducing refactoring referencing reflecting reformatting
refreshing registering regressing reimplementing reinforcing rejecting releasing relying
remaining remapping remembering removing renaming rendering repeating replacing reporting
representing requesting requiring researching resetting resizing resolving responding restarting
restoring restricting restructuring resulting retaining retrieving returning reusing reversing
reviewing revising revolving rewriting
sampling sandboxing satisfying scaffolding scaling scanning scheduling scoping scrolling
searching securing selecting sending separating sequencing serializing serving setting sharing
shaping shifting shortening showing signing simplifying simulating sizing skipping slicing
snapping sorting sourcing spacing spawning specializing specifying splitting sponsoring
stabilizing stacking staging standardizing starting stating stepping stopping storing streaming
strengthening stretching stringifying structuring styling submitting subscribing substituting
succeeding suggesting summarizing supervising supplying supporting suppressing surrounding
suspending sustaining swapping switching symbolizing synchronizing synthesizing
tabbing tagging targeting templating terminating testing texturing threading throttling toggling
tokenizing tooling tracing tracking trailing training transferring transforming transitioning
translating transmitting traversing treating triggering troubleshooting truncating tuning
tweaking typing
uncommenting undoing unifying unlocking unmounting unpacking unsubscribing unwinding updating
upgrading uploading using utilizing
validating valuing vectorizing verifying versioning viewing virtualizing visiting visualizing
waiting walking watching weighting welcoming wiring working worrying wrapping writing
yielding
zeroing zipping zooming

absence accessible accomplish accumulation activate acute adds adequate admiration
adorable adventure aesthetic affirmation afternoon aggregate alignment alleged alternate
amaze ambiguity angel annex anticipation anxiety apologize appetite archive ascending
assembly assert bargain beacon beauty behave benchmark blend bliss bloom blueprint bold
boundary breakthrough breathe bridge brilliant broadcast budget burden
calibrate campaign capable carbon cascade cautious certainty championship charming
charter chronicle circular clarity clever coalition cognitive command companion compassion
compile complement compound conceive concert concrete confident confront conquer consist
constraint contemplate contrast converge core cornerstone courtesy creative crux curriculum
daring deadline decisive defect definite deliberate delicate derive designate detect
dialogue dignity dimension diplomat diplomat disappoint distinctive doctrine dominant
draft durable duty
eagerly earnest eclipse elaborate elevate elegant eligible eloquent embrace emerge
emission emotional empathy emphasize empower encounter endure engagement enormous
enterprise enthusiasm entitle envision equality equate erosion essence eternal ethic
evolution exaggerate exceed excerpt exclusive exhaust exhibit exotic expedition explicit
exquisite extensive
fabric fable fascinate fate fellowship fierce finite flourish fluid forecast forge
formal foster franchise frontier fruitful furnish
gallery gauge genuine gesture glimpse governance gradient gratitude guardian
habitual harmony haste hazard heritage highlight hospitality humble hybrid hypothesis
ideal illuminate immense imminent impact imperial implication import impulse incentive
incline incompatible incredible indigenous infinite influential inherent initiative
innovative insight inspiration integral integrity intense intercept intermediate intimate
intricate intrinsic intuitive invariably invert ironic isolate
jewel jolt jubilant judgment junction
keen knack knit knot
landmark latitude launch lavish legacy legitimate leverage liberal limitless linear
locale lucid luminous luxury
majestic mandate mature maximize mediate medieval memorable mentor mercy metaphor
meticulous milestone miniature moderate momentum monopoly moral moreover municipal mutual
narrative necessity negotiate neutral noble nominate nurture
oath obey objective obscure obstacle obvious occasion offspring optimism orbit ordeal
outright oversight
paradox paramount participate patron peculiar penetrate perceive perpetual persist
perspective petition pioneer pivotal plausible pledge plunge portable portrait posture
potent precaution precise predominant preliminary premise prestige prevalent primitive
priority privilege profound progressive prohibit prolific prominent prompt proportion
prospect protocol provoke prudent punctual
quest quota
radius rally rational realm rebel reckon reconcile recreation refined reflect regime
reinforce reluctant remnant renaissance render repeal reservoir resilient restore
retaliate revelation rhythm rigid robust rotate rupture
sacred sanctuary saturate scaffold scrutiny secular seize sentiment sequence shelter
siege simulate skeptic solemn solidarity sovereign speculate sponsor stability stake
stimulate stipulate strain strategic streamline strive subordinate subscribe subsidy
substitute subtle summit supervise supplement surplus surrender sustain
tactic tangible tenure terrain testimony threshold thrive timely tolerance torch
tradition trajectory transform traverse tremendous tribunal tribute
unanimous undermine undertake unfold uniform unleash unprecedented uphold urgent utility
validate vanish versatile vibrant vigor violation virtue visionary vital vivid voluntary
vulnerable
warrant wholesale wisdom withdrawn worthy
yield

abrupt abundance accelerate acclaim accountable acute adjoining administer advent
affirm agenda alarm allocate ambassador amend ample anchor anthem apparatus appetite
arctic ascend aspire audit avert axis
backdrop ballot barren beacon bias bitter bolster breach brink broker
caliber canvas cascade catalyst cater certify chronicle civic clamp clarify cluster
coherent collapse collision colonial commence compact compel compile compound comprehend
conceive concise condemn confine conform confront consent consolidate conspire constrain
contemplate conversion convict coordinate corpus counsel crater credentials credible
culminate cumulative
debris decimal decisive decree default deficit defy delegate demolish deplete designate
detain deviate devise dialogue diminish diploma discord discrete disperse displace
distort divert doctrine dominance dose drainage drastic
elaborate electrode eligible embed embrace eminent emit enact endure engrave enhance
enrich enroll enterprise envision erode escalate ethanol evict evoke exert exempt exotic
extract
facade factual famine feat feud fiber flawed flaw flicker flock flora fluctuate forge
formidable foster fracture fragment frenzy frontier furnace
glacier gloom gradual granite gratitude grieve groundwork grove guardian gust
habitual hallmark hamper harness haven haze heir heritage hinder hollow homage
hypothesis
icicle ideology ignite illuminate immerse imminent impair implement implicit imposing
inadequate inaugurate incline incorporate induce inevitable infrastructure inhabitant
initiate inject inscribe insight inspect install intact intercept interim intern intrigue
invoke irrational irrigate isle
jeopardize jurisdiction
kinetic
lag lament lateral latitude legacy legislation liable likewise limestone linger literacy
locomotive lunar
maiden malfunction mandate manuscript maritime maximize medieval membrane migrate militia
momentum monarch monopoly mortal municipal
negate negligence negotiate nobility nominal norm notorious
oath obligate obscure onset orbit ore orient ornament outright overwhelm
pact palette panorama particle peculiar penal peninsula perceive peril peripheral persist
petition pier pivotal plausible plummet plunge pollute populace portable precede predicament
premise presume prevail prime proclaim procurement proficient prohibit prolific prominent
prone propagate prose prosperity provincial proximity prudent
quarantine quota
ratify realm rebound reconcile rectify redundant reign reinforce relay relentless
remnant repeal replicate reservoir resign resolution retract retrieve revolt revolve
rigid rite ritual rivalry rotation rupture
sanction scaffold scenic scrutiny secular sediment seize semester sensation serenity
shrink siege simulate slab slogan soar solitary sovereign specimen speculate sphere
stagnant staple statute stellar sterile stimulus stipulate stray stride stringent
sturdy subordinate subsidy substrate successor summon superb surge surplus swift
tempo terrain testimony textile threshold tidal token topology torment trait transcript
transplant traverse treaty tremor tribunal trivial tropical turbine turnover
uncover undermine underprivileged unearth unified unleash unrest unveil upheaval uphold
urbanize usher
vacancy veil vendor verify versatile vessel veto vicinity vigor vintage violate virtue
volatile voltage
warrant watershed welfare whirl wholesale wilderness wield wilt withstand
zeal zenith
words mat hat bat rat pat tap gap map nap cap lap rap wrap strap trap snap
`.trim();

export const DICTIONARY = new Set(
  (WORDS + ' ' + TECH_WORDS + ' ' + MORE_WORDS + ' ' + COMMON_EXTRAS + ' ' + TUTORIAL_WORDS + ' ' + SUPPLEMENTARY)
    .split(/\s+/)
    .filter(w => w.length > 0)
    .map(w => w.toLowerCase())
);

# KoodaustaJaKisailua2023FallClient
Client helper/wrapper for the koodausta ja kisailua 2023 fall event.

## Setup

### Venv

f you are not using a tool like PyCharm you need to manually create or move to the
virtual environment

Creating the virtual environment is done with python's venv module:
`python -m venv .\venv`

Depending on the tool you are using this might not open the virtual environment.
The virtual environment is open, if the command line feed starts with `(venv)`.
If creation doesn't open the venv, see next line.

If you have already created the venv but have closed the session after the 
creation of the venv or the venv has not opened, you need to open the venv with
a command. Assuming ps terminal, this can be done with the following command:

`.\venv\Scripts\Activate.ps1`

Other terminals should use the activate script in the same folder that corresponds with the terminal.

### Configs

Configs can be edited in `config.json` in the repository root. The configs here can
also be supplied as environment variables, if you for example want to create
multiple run configurations in PyCharm.

The client has the following configuration values:

 - `websocket_url`: the url of the game server websocket. Already configured
in the repository.
 - `token`: the unique token identifying your team. Already configured in the 
repository.
 - `bot_name`: the name of this bot. Is used to differentiate different bots from
the same team.
 - `wrapper_log_file`: the file into which the wrapper writes its logs. Can be
null to prevent wrapper from writing logs into a file. Default 'wrapper.log'.
Doesn't need to be identical to team AI log file.
 - `wrapper_log_stream`: the stream into which the wrapper writes its logs. Can
be null to prevent wrapper from writing logs into a stream. Can be 'stdout',
'stderr' or null. Default null.
 - `wrapper_log_level`: the minimum level of log entries to write from wrapper
logging. From least critical to most critical level, the options are 'DEBUG',
'INFO', 'WARNING', 'ERROR' and 'CRITICAL'. Default 'INFO'. If you want more
verbose feedback about the wrapper during runtime it's recommended to set this to
'DEBUG' and change the `wrapper_log_stream` config to 'stdout' or 'stderr'.
 - `team_ai_log_level`: the file into which the team AI writes its logs. Can be
null to prevent team AI from writing logs into a file. Default 'wrapper.log'.
Doesn't need to be identical to wrapper log file.
 - `team_ai_log_stream`: the stream into which the team AI writes its logs. Can
be null to prevent team AI from writing logs into a stream. Can be 'stdout',
'stderr' or null. Default stdout.
 - `team_ai_log_level`: the minimum level of log entries to write from wrapper
logging. From least critical to most critical level, the options are 'DEBUG',
'INFO', 'WARNING', 'ERROR' and 'CRITICAL'. Default 'DEBUG'.

## Running

To run the client websocket wrapper, run the python file `main.py` in the `src`
folder using the virtual environment's python executable. Both PyCharm and
VSCode know how to do this from the default run button so if you use either of
them you should not need to manually write the whole paths out.

## Editing the AI function

The AI function can be found in `src/team_ai`. It gets two parameters `context`
and `game_state` from the wrapper. It returns a `Command` object, or `None`. If
`None` is returned, it will be treated as a "move 0" command.

`game_state` is the present state of the game as seen by the ship.

`context` is a persistent object you can use to store data in. Context is wiped
at the start of a match, but preserved during the match. This means you are free
to add data to it to keep the data available through the match. If you want to use
type checking with context you can edit the `ClientContext` class in
`src/apiwrapper/websocket_wrapper`. By default `context` has two members.
`tick_length_ms` holds the value for max tick length. If you function takes longer
than max length - 50 milliseconds, the wrapper will return move 0 steps automatically.
`turn_rate` hold the maximum turn rate of the ship. The rate is given in 1/8ths of a
circle, so each value represents being able to turn one compass direction.

`Command` object should contain the type of the command (`Move`, `Turn` or `Shoot`)
and the command data.

If you want to log the behaviour inside the function you can use the `ai_logger`
object. Use methods `ai_logger.debug("message")`, `ai_logger.info("message")`,
`ai_logger.warning("message")`, `ai_logger.error("message")` and
`ai_logger.critical("message")` for the different levels of urgency in the log
messages.

Please note that there is a timeout of (tick_time - 50) milliseconds for the
function. This ensures the wrapper can send a command every tick.

# Models

Model data can be found in MODELS.md



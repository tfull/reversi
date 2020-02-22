require 'socket'
require 'yaml'

DEFAULT_BOARD_SIZE = 8

def piece?(s)
  s == "x" || s == "o"
end

def opposite_piece(piece)
  case piece
  when "x" then
    "o"
  when "o" then
    "x"
  else
    nil
  end
end

class GameError < StandardError
end

class Game
  attr_reader :board_size

  def initialize(board_size)
    @buffer = ""
    @board_size = board_size
    @board = new_board(board_size)
  end

  def new_board(size)
    board = Array.new(size).map{ |_| Array.new(size, ".") }
    board[size / 2 - 1][size / 2 - 1] = "x"
    board[size / 2 - 1][size / 2] = "o"
    board[size / 2][size / 2 - 1] = "o"
    board[size / 2][size / 2] = "x"
    board
  end

  def get_board_string
    @board.map{ |row| row.join("") }.join("")
  end

  def command_put(piece, location)
    raise GameError.new("command_put") if (location =~ /^[A-H][1-8]$/).nil?
    y = location[0].ord - "A".ord
    x = location[1].ord - "1".ord
    put(piece, x, y)
  end

  def valid_board_range(x, y)
    0 <= x && x < @board_size && 0 <= y && y < @board_size
  end

  def put(piece, x, y, test=false)
    if @board[y][x] != "."
      if test
        return false
      else
        raise GameError.new("illegal put")
      end
    end

    targets = []

    for dy in [-1, 0, 1]
      for dx in [-1, 0, 1]
        next if dx == 0 && dy == 0
        px = x + dx
        py = y + dy
        next unless valid_board_range(px, py)
        next unless @board[py][px] == opposite_piece(piece)
        targets_direction = []
        begin
          targets_direction << { x: px, y: py }
          px += dx
          py += dy
        end while valid_board_range(px, py) && @board[py][px] == opposite_piece(piece)
        if valid_board_range(px, py) && @board[py][px] == piece
          targets << targets_direction
        end
      end
    end

    moves = targets.flatten
    if moves.size == 0
      if test
        false
      else
        raise GameError.new("invalid move")
      end
    else
      unless test
        moves.each do |move|
          @board[move[:y]][move[:x]] = piece
        end
        @board[y][x] = piece
      end
      true
    end
  end

  def movable(piece)
    for y in 0...@board_size
      for x in 0...@board_size
        return true if put(piece, x, y, true)
      end
    end
    false
  end

  def count_piece(piece)
    count = 0
    for y in 0...@board_size
      for x in 0...@board_size
        count += 1 if @board[y][x] == piece
      end
    end
    count
  end

  def get_information
    info = { }
    for piece in ["o", "x"]
      info[piece] = count_piece(piece)
    end
    info
  end

  def print_board
    puts "  #{(1..@board_size).map{ |x| x.to_s }.join}"
    puts "-+#{'-' * @board_size}"
    for y in 0...@board_size
      puts "#{("A".ord + y).chr}#{@board[y].join}"
    end
  end

  def finish
    get_information
  end
end

class Connection
  def initialize(port)
    @port = port
    @server = nil
    @clients = nil
    @buffers = nil
    @pieces = nil
    @game = nil
    @board_size = nil
  end

  def open_connection
    @server = TCPServer.open(@port)

    @clients = []
    @buffers = []
    2.times do |i|
      @clients << @server.accept
      @buffers << ""
    end
  end

  def close_connection
    @clients.each do |client|
      client.close
    end
    @server.close
  end

  def send(index, property)
    @clients[index].puts(YAML.dump(property) + "\n")
  end

  def receive(index)
    while true
      ix = @buffers[index].index("\n\n")
      unless ix.nil?
        entity = @buffers[index][0...(ix + 2)]
        @buffers[index] = @buffers[index][(ix + 2)..-1]
        return YAML.load(entity)
      end
      @buffers[index] += @clients[index].recv(1024)
    end
  end

  def game_loop
    piece = "x"

    while true
      @game.print_board
      index = @pieces.index{ |x| x == piece }
      opposite_index = 1 - index
      puts "piece=#{piece}"

      if @game.movable(piece)
        send(index, {
          "status" => "you",
          "board_string" => @game.get_board_string
        })
        send(opposite_index, {
          "status" => "opposite",
          "board_string" => @game.get_board_string
        })

        entry = receive(index)
        raise "not move" if entry["status"] != "move"
        code = entry["code"]
        @game.command_put(piece, code)

        send(index, {
          "status" => "move",
          "code" => code
        })
        send(opposite_index, {
          "status" => "move",
          "code" => code
        })

        piece = opposite_piece(piece)
      else
        if @game.movable(opposite_piece(piece))
          send(index, {
            "status" => "you",
            "board_string" => @game.get_board_string
          })
          send(opposite_index, {
            "status" => "opposite",
            "board_string" => @game.get_board_string
          })

          entry = receive(index)
          raise "not move" if entry["status"] != "move"
          raise "not movable" if entry["code"] != "pass"

          send(index, {
            "status" => "move",
            "code" => "pass"
          })
          send(opposite_index, {
            "status" => "move",
            "code" => "pass"
          })

          piece = opposite_piece(piece)
        else
          info = @game.finish
          info["status"] = "finish"
          you_info = info.clone
          opposite_info = info.clone

          if info[piece] > info[opposite_piece(piece)]
            you_info["result"] = "win"
            opposite_info["result"] = "lose"
          elsif info[piece] < info[opposite_piece(piece)]
            you_info["result"] = "lose"
            opposite_info["result"] = "win"
          else
            you_info["result"] = "draw"
            opposite_info["result"] = "draw"
          end
          send(index, you_info)
          send(opposite_index, opposite_info)
          return
        end
      end
    end
  end

  def main_loop
    send_connected
    send_request
    receive_request
    send_start
    game_loop
    puts "done"
  end

  def send_connected
    2.times do |index|
      property = { "status" => "connected" }
      send(index, property)
    end
  end

  def send_request
    2.times do |index|
      property = { "status" => "request", "columns" => ["piece", "board_size"] }
      send(index, property)
    end
  end

  def receive_request
    entries = [nil, nil]
    2.times do |index|
      entries[index] = receive(index)
    end
    @pieces = allocate_pieces(entries)
    @board_size = determine_board_size(entries)
  end

  def allocate_pieces(entries)
    ps = entries.map{ |e| e["piece"] }
    if piece?(ps[0]) && opposite_piece(ps[0]) == ps[1]
      ps
    elsif piece?(ps[0]) && ! piece?(ps[1])
      ps[1] = opposite_piece(ps[0])
      ps
    elsif piece?(ps[1]) && ! piece?(ps[0])
      ps[0] = opposite_piece(ps[1])
      ps
    else
      ["x", "o"].shuffle
    end
  end

  def determine_board_size(entries)
    xs = entries.map{ |e| e["board_size"] }
    if ! xs[0].nil? && ! xs[1].nil?
      if xs[0] == xs[1]
        xs[0]
      else
        DEFAULT_BOARD_SIZE
      end
    elsif ! xs[0].nil?
      xs[0]
    elsif ! xs[1].nil?
      xs[1]
    else
      DEFAULT_BOARD_SIZE
    end
  end

  def send_start
    2.times do |index|
      @game = Game.new(@board_size)
      property = {
        "status" => "start",
        "piece" => @pieces[index],
        "board_size" => @game.board_size,
        "board_string" => @game.get_board_string
      }
      send(index, property)
    end
  end
end

def main(port)
  connection = Connection.new(port)
  connection.open_connection
  connection.main_loop
  connection.close_connection
end

if $0 == __FILE__
  main(ARGV[0].to_i)
end

#include <deque>
#include <string>
#include <vector>

struct SerialProtocol {
    std::deque <char> buffer;

    std::vector<std::string> on_packet_recv(const std::string& data);
    std::string send_packet(const std::string& data);
};

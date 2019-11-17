#include "gtest/gtest.h"
#include "BufferProtocol.h"
#include <iostream>
#include <bitset>
#include <string>
#include <queue>

using namespace std;

queue <char> read_buffer;
queue <char> write_buffer;

void init_serial_protocol() {
    read_buffer = {};
    write_buffer = {};
}

void write_to_read_buffer(const string& str) {
    for (auto &&x : str) read_buffer.push(x);
}

string read_from_write_buffer() {
    string x;
    while (!write_buffer.empty()) {
        x.push_back(write_buffer.front());
        // cout << bitset<8>(write_buffer.front()) << endl;
        write_buffer.pop();
    }
    return x;
}

char SerialProtocol::read() {
    char ch = read_buffer.front();
    read_buffer.pop();
    return ch;
}

void SerialProtocol::write(char ch) {
    write_buffer.push(ch);
}

class BufferProtocolTest : public ::testing::Test {
protected:
    BufferProtocolTest() : bp(&sp) {}
    void SetUp() override {
        init_serial_protocol();
    }
    SerialProtocol sp;
    BufferProtocol bp;
};

TEST_F(BufferProtocolTest, ConstructAndDestruct) {
    BufferProtocol bp(&sp);
}

TEST_F(BufferProtocolTest, ReadWriteOneByte) {
    bp.begin();
    bp.write(0xff);
    bp.end();
    write_to_read_buffer(read_from_write_buffer());
    EXPECT_EQ(bp.read(), -1);
    EXPECT_EQ(bp.read(), 0xff);
}

TEST_F(BufferProtocolTest, ReadWriteBytes) {
    for (int i = 0; i < 32; i++) {
        bp.begin();
        for (int j = 0; j <= i; j++) bp.write(j * 5);
        bp.end();
    }
    write_to_read_buffer(read_from_write_buffer());
    for (int i = 0; i < 32; i++) {
        ASSERT_EQ(bp.read(), -1);
        for (int j = 0; j <= i; j++) ASSERT_EQ(bp.read(), j * 5);
        ASSERT_EQ(bp.read(), -1);
    }
}
